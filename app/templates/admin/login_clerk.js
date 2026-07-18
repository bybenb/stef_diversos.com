const PUBLISHABLE_KEY = 'pk_test_c3VtbWFyeS1ha2l0YS04OS5jbGVyay5hY2NvdW50cy5kZXYk'; 
                        

if (!PUBLISHABLE_KEY || PUBLISHABLE_KEY === '') {
    document.getElementById('clerk-sign-in').innerHTML = 
        '<div class="alert alert-danger">ERRO: Chave Publishable Key não configurada no arquivo HTML!</div>';
    console.error('Clerk: Publishable Key não definida!');
} else {
    const clerk = new Clerk(PUBLISHABLE_KEY);
    
    clerk.load().then(() => {
        // Monta o componente de login na div
        const signInElement = document.getElementById('clerk-sign-in');
        clerk.mountSignIn(signInElement, {
            afterSignInUrl: '/admin/dashboard', // Redireciona após login
            signUpUrl: 'https://clerk.com/sign-up' // Opcional
        });
    }).catch(err => {
        console.error('Erro ao carregar Clerk:', err);
        document.getElementById('clerk-sign-in').innerHTML = 
            '<div class="alert alert-danger">Erro ao carregar Clerk. Verifique o console.</div>';
    });
}
