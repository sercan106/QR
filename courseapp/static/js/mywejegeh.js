
// Büyüteç simgesine tıklanırsa formu göster
document.getElementById('xxx').addEventListener('click', function(event) {
  // Varsayılan davranışı engelle (yani sayfanın başka bir sayfaya yönlendirilmesini engelle)
  event.preventDefault();
  document.getElementById('kutu').classList.remove('hidden');
  document.getElementById('xxx').style.display = 'none';
});

// Çarpı butonuna tıklanırsa formu gizle
document.getElementById('closeSearchBtn').addEventListener('click', function() {
  document.getElementById('kutu').classList.add('hidden');
  document.getElementById('xxx').style.display = 'block';
});








/* anasayfadaki ileri geri alanı takvim içinde */

let currentItemIndex = 0;
const items = document.getElementsByClassName('item');

function ileri() {
  items[currentItemIndex].style.display = 'none';
  currentItemIndex = (currentItemIndex + 1) % items.length;
  items[currentItemIndex].style.display = 'block';
}

function geri() {
  items[currentItemIndex].style.display = 'none';
  currentItemIndex = (currentItemIndex - 1 + items.length) % items.length;
  items[currentItemIndex].style.display = 'block';
}
for (let i = 1; i < items.length; i++) {
  items[i].style.display = 'none';
}



// /* projeler üzerine gelince  */
// const pro = document.getElementById('pro');/* id seçimi */
// const div2 = document.getElementById('k');/* id seçimi */
// const div3 = document.querySelector('.child-div');/* clasname seçimi */

// pro.addEventListener('mouseover', function () {
//      div3.style.display = 'block';
//      div2.style.display = 'none';
   
// });

// pro.addEventListener('mouseout', function () {
//   div3.style.display = 'none';
//   div2.style.display = 'block';

// });


/* projelerde ki resimleri değiştirmek içn */
function changeImage(src) {
  var dynamicImage = document.getElementById('dynamicImage');
  dynamicImage.style.opacity = "0";
  setTimeout(function() {
    dynamicImage.src = src;
    dynamicImage.style.opacity = "1";
  }, 300);
}






/* _________________________resim ___________________ */
let myImage = document.getElementById('myImage');

myImage.addEventListener('mouseover', function() {
  myImage.style.transform = 'scale(1.1)';
});

myImage.addEventListener('mouseleave', function() {
  myImage.style.transform = 'scale(1.0)';
});











//_______________________________________LOGOLAR_________________________

// image-container classına sahip bütün div'leri seç
let imageContainers = document.querySelectorAll('.image-container');

// Her bir div üzerinden geç
imageContainers.forEach(function(container) {
    // Her bir div içindeki image-1 ve image-2 classına sahip img elementlerini seç
    let image1 = container.querySelector('.image-1');
    let image2 = container.querySelector('.image-2');

    // Div'e mouseover event listener ekleyerek image1'i gizle ve image2'yi göster
    container.addEventListener('mouseover', function() {
        image1.style.display = 'none';
        image2.style.display = 'block';
    });

    // Div'e mouseout event listener ekleyerek image1'i göster ve image2'yi gizle
    container.addEventListener('mouseout', function() {
        image1.style.display = 'block';
        image2.style.display = 'none';
    });
});















