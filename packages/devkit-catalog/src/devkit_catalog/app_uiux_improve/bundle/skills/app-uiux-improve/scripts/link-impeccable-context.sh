#!/bin/sh
# Run through sh. Mutating setup requires quiescent managed entries and source.

mode=link
problem=0
owns_lock=no
newline='
'
export GIT_OPTIONAL_LOCKS=0
unset CLICOLOR CLICOLOR_FORCE LS_COLORS

result() {
    printf '[CONTEXT_LINK_RESULT: mode=%s code=%s exit=%s action=%s]\n' "$mode" "$1" "$2" "$3"
    exit "$2"
}
fail() {
    printf '[DETAIL: code=%s action=%s]\n' "$1" "$2" >&2
    result "$1" 2 "$2"
}
cleanup() {
    if [ "$owns_lock" = yes ]; then
        rmdir "$lock" 2>/dev/null || :
    fi
}
trap cleanup 0
trap 'fail LINK_IO_FAILED CHECK_PERMISSIONS' HUP INT TERM

if [ "${1-}" = --check ]; then
    mode=check
    shift
fi
if [ "${1-}" = -- ]; then
    shift
elif [ "${1#-}" != "${1-}" ]; then
    fail LINK_ARGUMENT_INVALID FIX_INPUT
fi
[ "$#" -le 1 ] || fail LINK_ARGUMENT_INVALID FIX_INPUT
source_arg=${1-docs/materials/impeccable}
[ -n "$source_arg" ] || fail LINK_SOURCE_INVALID FIX_SOURCE

# Sentinels preserve every path byte, including trailing newline bytes.
root=$(git rev-parse --show-toplevel 2>/dev/null && printf x) || fail LINK_NOT_WORKTREE USE_WORKTREE
root=${root%x}
root=${root%"$newline"}
cd -P "$root" 2>/dev/null || fail LINK_NOT_WORKTREE USE_WORKTREE
root=$(pwd -P && printf x) || fail LINK_NOT_WORKTREE USE_WORKTREE
root=${root%x}
root=${root%"$newline"}
setting=$(git config --bool core.symlinks 2>/dev/null)
[ "$setting" != false ] || fail LINK_SYMLINKS_DISABLED ENABLE_SYMLINKS
case "$source_arg" in
    /*) candidate=$source_arg ;;
    *) candidate=$root/$source_arg ;;
esac
source=$(CDPATH= cd -P "$candidate" 2>/dev/null && pwd -P && printf x) || fail LINK_SOURCE_INVALID FIX_SOURCE
source=${source%x}
source=${source%"$newline"}
case "$source" in
    "$root"/*) relative=${source#"$root"/} ;;
    *) fail LINK_SOURCE_INVALID FIX_SOURCE ;;
esac
# These bytes cannot be represented by the one-line path inspection contract.
case "$source" in *"$newline"*) fail LINK_SOURCE_INVALID FIX_SOURCE ;; esac
if printf '%s' "$source" | LC_ALL=C grep '[[:cntrl:]]' >/dev/null 2>&1; then
    fail LINK_SOURCE_INVALID FIX_SOURCE
fi
metadata=$(git rev-parse --absolute-git-dir 2>/dev/null && printf x) || fail LINK_NOT_WORKTREE USE_WORKTREE
metadata=${metadata%x}
metadata=${metadata%"$newline"}
case "$source" in
    "$root/.git"|"$root/.git/"*|"$metadata"|"$metadata/"*) fail LINK_SOURCE_INVALID FIX_SOURCE ;;
esac
for entry in PRODUCT.md DESIGN.md .impeccable; do
    path=$source/$entry
    [ ! -L "$path" ] || fail LINK_SOURCE_INVALID FIX_SOURCE
    if [ -e "$path" ]; then
        if [ "$entry" = .impeccable ]; then
            [ -d "$path" ] && [ -r "$path" ] && [ -x "$path" ] || fail LINK_SOURCE_INVALID FIX_SOURCE
        else
            [ -f "$path" ] && [ -r "$path" ] || fail LINK_SOURCE_INVALID FIX_SOURCE
        fi
    fi
done
exclude=$(git rev-parse --git-path info/exclude 2>/dev/null && printf x) || fail LINK_NOT_WORKTREE USE_WORKTREE
exclude=${exclude%x}
exclude=${exclude%"$newline"}
case "$exclude" in /*) ;; *) exclude=$root/$exclude ;; esac
if [ -e "$exclude" ]; then
    [ -f "$exclude" ] && [ -r "$exclude" ] || fail LINK_IO_FAILED CHECK_PERMISSIONS
fi
need_exclude=no
for entry in PRODUCT.md DESIGN.md .impeccable; do
    if [ ! -f "$exclude" ] || ! grep -F -x -e "/$entry" "$exclude" >/dev/null 2>&1; then
        need_exclude=yes
    fi
done
if [ "$mode" = link ] && [ "$need_exclude" = yes ]; then
    mkdir -p "${exclude%/*}" 2>/dev/null || fail LINK_IO_FAILED CHECK_PERMISSIONS
    lock=$exclude.impeccable-context.lock
    if ! mkdir "$lock" 2>/dev/null; then
        if [ -e "$lock" ] || [ -L "$lock" ]; then
            fail LINK_EXCLUDE_BUSY RETRY_AFTER_UNLOCK
        fi
        fail LINK_IO_FAILED CHECK_PERMISSIONS
    fi
    owns_lock=yes
fi

link_state() {
    code=$1
    action=$2
    content=${3-}
    if [ -n "$content" ]; then
        printf '[CONTEXT_LINK: %s code=%s content=%s action=%s]\n' "$entry" "$code" "$content" "$action"
    else
        printf '[CONTEXT_LINK: %s code=%s action=%s]\n' "$entry" "$code" "$action"
    fi
    [ "$action" = NONE ] || problem=1
}
for entry in PRODUCT.md DESIGN.md .impeccable; do
    path=$source/$entry
    root_entry=./$entry
    expected=$relative/$entry
    tracked=$(git ls-files -- "$entry" 2>/dev/null && printf x) || fail LINK_INSPECTION_FAILED INSPECT_FILES
    tracked=${tracked%x}
    if [ -n "$tracked" ]; then
        link_state LINK_TRACKED UNTRACK_MANUALLY
    elif [ ! -e "$path" ]; then
        if [ -L "$root_entry" ]; then
            link_state LINK_STALE INSPECT_LINK
        elif [ -e "$root_entry" ]; then
            link_state LINK_OCCUPIED INSPECT_ROOT
        else
            link_state LINK_ABSENT NONE
        fi
    elif [ ! -e "$root_entry" ] && [ ! -L "$root_entry" ]; then
        if [ "$mode" = check ]; then
            link_state LINK_MISSING RUN_LINK
        else
            ln -s -- "$expected" "$root_entry" 2>/dev/null || fail LINK_IO_FAILED CHECK_PERMISSIONS
            link_state LINK_CREATED NONE
        fi
    elif [ ! -L "$root_entry" ]; then
        content=type_mismatch
        if [ -f "$root_entry" ] && [ -f "$path" ]; then
            cmp -s "$path" "$root_entry"
            comparison=$?
            case "$comparison" in 0) content=equal ;; 1) content=differs ;; *) fail LINK_INSPECTION_FAILED INSPECT_FILES ;; esac
        elif [ -d "$root_entry" ] && [ -d "$path" ]; then
            diagnostic=$(git -c core.filemode=false diff --no-index --exit-code --no-ext-diff --no-textconv -- "$path" "$root_entry" 2>&1 >/dev/null)
            comparison=$?
            [ -z "$diagnostic" ] || fail LINK_INSPECTION_FAILED INSPECT_FILES
            case "$comparison" in 0) content=equal ;; 1) content=differs ;; *) fail LINK_INSPECTION_FAILED INSPECT_FILES ;; esac
        fi
        link_state LINK_REPLACED MERGE_INTO_SOURCE "$content"
    elif [ ! -e "$root_entry" ]; then
        link_state LINK_DANGLING INSPECT_LINK
    else
        listing=$(LC_ALL=C QUOTING_STYLE=literal ls -dn "$root_entry" 2>/dev/null && printf x) || fail LINK_INSPECTION_FAILED INSPECT_FILES
        listing=${listing%x}
        listing=${listing%"$newline"}
        marker=" $root_entry -> "
        case "$listing" in
            *"$marker"*) target=${listing#*"$marker"} ;;
            *) fail LINK_INSPECTION_FAILED INSPECT_FILES ;;
        esac
        if [ "$target" = "$expected" ]; then
            link_state LINK_OK NONE
        else
            link_state LINK_WRONG_TARGET INSPECT_LINK
        fi
    fi
done

for entry in PRODUCT.md DESIGN.md .impeccable; do
    pattern=/$entry
    if [ -f "$exclude" ]; then
        grep -F -x -e "$pattern" "$exclude" >/dev/null 2>&1
        found=$?
        [ "$found" -le 1 ] || fail LINK_IO_FAILED CHECK_PERMISSIONS
    else
        found=1
    fi
    if [ "$found" -eq 0 ]; then
        code=EXCLUDE_OK
        action=NONE
    elif [ "$mode" = check ]; then
        code=EXCLUDE_MISSING
        action=RUN_LINK
        problem=1
    else
        if [ -s "$exclude" ]; then
            last=$(tail -c 1 "$exclude" 2>/dev/null && printf x) || fail LINK_IO_FAILED CHECK_PERMISSIONS
            if [ "$last" != "${newline}x" ]; then
                printf '\n' >> "$exclude" || fail LINK_IO_FAILED CHECK_PERMISSIONS
            fi
        fi
        printf '%s\n' "$pattern" >> "$exclude" || fail LINK_IO_FAILED CHECK_PERMISSIONS
        code=EXCLUDE_ADDED
        action=NONE
    fi
    printf '[CONTEXT_EXCLUDE: %s code=%s action=%s]\n' "$entry" "$code" "$action"
done
[ "$problem" -eq 0 ] || result LINK_PROBLEMS 1 INSPECT_REPORTED
result LINK_CLEAN 0 NONE
