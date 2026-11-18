'use strict';
const root=document.documentElement;
const themeButton=document.getElementById('themeToggle');
themeButton.addEventListener('click',()=>{
  const dark=root.dataset.theme!=='dark';root.dataset.theme=dark?'dark':'light';
  themeButton.textContent=dark?'浅色':'深色';themeButton.setAttribute('aria-pressed',String(dark));
  themeButton.setAttribute('aria-label',dark?'切换到浅色主题':'切换到深色主题');
});
const asset='skills/endfield-design-kit/assets/';
const previews={
  web:{image:asset+'preview-web.jpg',alt:'浅色终末地风格工作台预览',caption:'浅色网页：记录选择、曲线和表格共用清楚的层级。',href:asset+'web/index.html',label:'打开交互示例 ↗'},
  dark:{image:asset+'preview-web-dark.jpg',alt:'深色终末地风格工作台预览',caption:'深色网页：保留完整的文字、表格与状态对比。',href:asset+'web/index.html',label:'打开交互示例 ↗'},
  slides:{image:asset+'preview-slides.webp',alt:'六种可编辑 PPT 版式预览',caption:'六类可编辑版式，图表自带数据工作簿。',href:asset+'slides/yellow-paper-template.pptx',label:'下载 PPT 模板 ↓'}
};
document.querySelectorAll('[data-preview]').forEach(button=>button.addEventListener('click',()=>{
  const value=previews[button.dataset.preview];if(!value)return;
  const image=document.getElementById('previewImage'),link=document.getElementById('previewOpen');
  image.src=value.image;image.alt=value.alt;document.getElementById('previewCaption').textContent=value.caption;
  link.href=value.href;link.textContent=value.label;
  if(button.dataset.preview==='slides')link.setAttribute('download','');else link.removeAttribute('download');
  document.querySelectorAll('[data-preview]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
}));
const commands={project:'npx skills add zhendenanbeng/endfild-ui --skill endfield-design-kit',codex:'npx skills add zhendenanbeng/endfild-ui --skill endfield-design-kit -a codex -g'};
document.querySelectorAll('[data-install]').forEach(button=>button.addEventListener('click',()=>{
  document.getElementById('installCommand').textContent=commands[button.dataset.install];
  document.querySelectorAll('[data-install]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
  document.getElementById('copyStatus').textContent='选择已更新，可复制当前安装命令。';
}));
document.getElementById('copyCommand').addEventListener('click',async()=>{
  const code=document.getElementById('installCommand'),status=document.getElementById('copyStatus');
  try{
    if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(code.textContent);status.textContent='已复制安装命令。';
  }catch{
    const range=document.createRange();range.selectNodeContents(code);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);
    status.textContent='命令已选中，请按 Ctrl+C 或 Command+C 复制。';
  }
});
