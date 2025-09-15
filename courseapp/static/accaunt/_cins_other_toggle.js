// Toggle 'Diğer' input for breed
(function(){
  const cins = document.getElementById('id_cins');
  let otherInput = document.getElementById('id_cins_diger');
  if (!cins || !otherInput) return;
  const update = () => {
    const show = cins.value === '__OTHER__';
    const wrap = otherInput.closest('.form-group') || otherInput.parentElement;
    if (wrap) wrap.style.display = show ? '' : 'none';
    if (!show) otherInput.value = '';
  };
  cins.addEventListener('change', update);
  update();
})();

