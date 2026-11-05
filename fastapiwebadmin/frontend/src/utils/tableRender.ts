import { h, type VNode } from 'vue';
import { ElButton, type ButtonProps } from 'element-plus';
import { auth as authFunction } from '/@/utils/authFunction';

export interface TableActionItem {
	label: string;
	type?: ButtonProps['type'];
	auth?: string;
	onClick: () => void;
}

/** 表格操作列：link 按钮 + 自动换行，与 ntesterc 列表风格一致 */
export function renderTableActions(buttons: TableActionItem[]): VNode {
	const nodes = buttons
		.filter((btn) => !btn.auth || authFunction(btn.auth))
		.map((btn) =>
			h(
				ElButton,
				{
					link: true,
					type: btn.type ?? 'primary',
					onClick: btn.onClick,
				},
				() => btn.label
			)
		);
	return h('div', { class: 'synrebort-table-actions' }, nodes);
}

export function resolveColumnWidth(col: Record<string, unknown>): string | number | undefined {
	const w = col.width;
	if (w === '' || w === undefined || w === null) return undefined;
	return w as string | number;
}

export function resolveColumnMinWidth(col: Record<string, unknown>): number | undefined {
	if (col.minWidth) return Number(col.minWidth);
	if (col.label === '操作') return 240;
	if (!resolveColumnWidth(col)) return 120;
	return undefined;
}

export function isOperationColumn(col: Record<string, unknown>): boolean {
	return col.label === '操作';
}
