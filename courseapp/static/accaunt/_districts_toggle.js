// Dynamic districts for province selection (step 3)
(function(){
  const il = document.getElementById('id_il');
  const ilce = document.getElementById('id_ilce');
  if (!il || !ilce) return;
  async function loadDistricts(ilId){
    ilce.innerHTML = '<option value="">Seçiniz</option>';
    if (!ilId) return;
    try{
      const resp = await fetch('/accaunt/register/districts/?il_id=' + ilId);
      const data = await resp.json();
      (data.items || []).forEach(function(item){
        const opt = document.createElement('option');
        opt.value = item.id;
        opt.textContent = item.ad;
        ilce.appendChild(opt);
      });
    }catch(e){}
  }
  il.addEventListener('change', function(){ loadDistricts(this.value); });
  if (il.value) loadDistricts(il.value);
})();
