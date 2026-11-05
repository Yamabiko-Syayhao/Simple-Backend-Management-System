import {
	initSetStyle,
	onAddFilterChange,
	onWartermarkChange,
} from '/@/layout/navBars/topBar/settings/index';

export function initThemeStylesOnBoot(config: ThemeConfigState['themeConfig']) {
	if (config.isGrayscale) onAddFilterChange('grayscale');
	if (config.isInvert) onAddFilterChange('invert');
	if (config.isWartermark) onWartermarkChange();
	initSetStyle();
}
