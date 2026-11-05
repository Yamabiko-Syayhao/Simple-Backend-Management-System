import { nextTick } from 'vue';
import { fourDotsSpinnerHtml } from '/@/assets/svg/loading';
import '/@/theme/loading.scss';

const LOADING_ID = 'app-page-loading';

const getLoadingElement = (): HTMLElement | null => document.getElementById(LOADING_ID);

const createLoadingElement = (): HTMLElement => {
	const el = document.createElement('div');
	el.id = LOADING_ID;
	el.className = 'app-page-loading';
	el.innerHTML = fourDotsSpinnerHtml;
	document.body.appendChild(el);
	return el;
};

export const loadingService = {
	show(): () => void {
		const el = getLoadingElement() ?? createLoadingElement();
		el.style.display = 'flex';
		window.nextLoading = true;
		return () => this.hide();
	},
	hide(): void {
		const el = getLoadingElement();
		if (el) {
			el.style.display = 'none';
		}
		window.nextLoading = false;
	},
};


export const NextLoading = {
	start: () => {
		loadingService.show();
	},
	done: (time: number = 0) => {
		nextTick(() => {
			setTimeout(() => {
				loadingService.hide();
			}, time);
		});
	},
};
