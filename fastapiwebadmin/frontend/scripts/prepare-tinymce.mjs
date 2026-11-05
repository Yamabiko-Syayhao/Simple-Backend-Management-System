import { cpSync, mkdirSync } from 'node:fs';
mkdirSync('public/tinymce', { recursive: true });
cpSync('node_modules/tinymce', 'public/tinymce', { recursive: true });
mkdirSync('public/tinymce/langs', { recursive: true });
cpSync(
  'node_modules/tinymce-i18n/langs7/zh_CN.js',
  'public/tinymce/langs/zh_CN.js'
);
