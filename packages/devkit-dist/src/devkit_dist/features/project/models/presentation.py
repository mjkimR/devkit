"""Resolved response-language preference and the warning for an unsupported requested value."""

from dataclasses import dataclass

from devkit.advisory import Actor, AdvisoryError, Level, Retry

# Exact ``[presentation] language`` values; any other string resolves to ``en`` with a visible warning.
PRESENTATION_LANGUAGES = ("auto", "en", "ko")


@dataclass(frozen=True)
class PresentationLanguage:
    requested: str
    resolved: str
    source: str
    fallback: bool

    @property
    def approval_language(self) -> str:
        return "ko" if self.resolved == "ko" else "en"


class PresentationLanguageUnsupportedNotice(AdvisoryError):
    """A ``[presentation] language`` value other than ``auto``, ``en`` or ``ko`` resolved to ``en``; never raised.

    ``devkit sync``, ``devkit status`` and ``devkit config show`` return it under ``notices`` so the English
    fallback is never silent.
    """

    code = "PRESENTATION_LANGUAGE_UNSUPPORTED"
    level = Level.WARNING
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True

    @classmethod
    def of(cls, language: PresentationLanguage) -> "PresentationLanguageUnsupportedNotice":
        accepted = ", ".join(PRESENTATION_LANGUAGES)
        return cls(
            f"{language.source}: presentation.language {language.requested!r} is unsupported; "
            f"it resolves to {language.resolved!r}",
            fix=f"Set [presentation] language in {language.source} to one of: {accepted}",
            target_files=[language.source],
        )
