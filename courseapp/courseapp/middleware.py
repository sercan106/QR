from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

class ProfileCompletionMiddleware:
    """
    Kullanıcı giriş yapmışsa ama veteriner/petshop profili eksikse
    ilgili profil tamamlama sayfasına yönlendirir.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        u = request.user
        if u.is_authenticated and not request.path.startswith("/admin/"):
            # Veteriner
            if hasattr(u, "veteriner_profili"):
                v = u.veteriner_profili
                if not v.il or not v.adres_detay:
                    try:
                        url = reverse("veteriner:veteriner_profil_tamamla")
                    except NoReverseMatch:
                        url = "/veteriner/profil-tamamla/"
                    if not request.path.startswith(url):
                        return redirect(url)

            # Petshop
            if hasattr(u, "petshop_profili"):
                s = u.petshop_profili
                if not s.il or not s.adres_detay:
                    try:
                        url = reverse("petshop:petshop_profil_tamamla")
                    except NoReverseMatch:
                        url = "/petshop/profil-tamamla/"
                    if not request.path.startswith(url):
                        return redirect(url)

        return self.get_response(request)
