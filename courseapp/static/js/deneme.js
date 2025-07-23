const openSearchBtn = document.getElementById('openSearchBtn');
const closeSearchBtn = document.getElementById('closeSearchBtn');
const searchForm = document.getElementById('searchForm');

openSearchBtn.addEventListener('click', () => {
    searchForm.classList.remove('hidden');
});

closeSearchBtn.addEventListener('click', () => {
    searchForm.classList.add('hidden');
});