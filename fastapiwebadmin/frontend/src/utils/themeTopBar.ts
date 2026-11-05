export const DARK_TOP_BAR_BG = '#191919';
export const DARK_TOP_BAR_COLOR = '#dadada';

export function applyDarkTopBarColors() {
	document.documentElement.style.setProperty('--next-bg-topBar', DARK_TOP_BAR_BG);
	document.documentElement.style.setProperty('--next-bg-topBarColor', DARK_TOP_BAR_COLOR);
}

export function applyLightTopBarColors(topBar: string, topBarColor: string) {
	document.documentElement.style.setProperty('--next-bg-topBar', topBar);
	document.documentElement.style.setProperty('--next-bg-topBarColor', topBarColor);
}

export function syncDocumentThemeMode(isDark: boolean, topBar = '#ffffff', topBarColor = '#606266') {
	const html = document.documentElement;
	if (isDark) {
		html.setAttribute('data-theme', 'dark');
		applyDarkTopBarColors();
		return;
	}
	html.setAttribute('data-theme', '');
	applyLightTopBarColors(topBar, topBarColor);
}
