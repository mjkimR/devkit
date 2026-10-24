export class ThemeState {
	current = $state<'dark' | 'light'>('dark');

	sync(themeProp?: string) {
		if (themeProp === 'light' || themeProp === 'dark') {
			this.current = themeProp;
		} else if (typeof localStorage !== 'undefined') {
			const saved = localStorage.getItem('sdd-theme');
			if (saved === 'light' || saved === 'dark') {
				this.current = saved;
			}
		}
	}

	set(theme: 'dark' | 'light') {
		this.current = theme;
		try {
			localStorage?.setItem('sdd-theme', theme);
		} catch {}
	}

	toggle() {
		this.set(this.current === 'dark' ? 'light' : 'dark');
	}
}
