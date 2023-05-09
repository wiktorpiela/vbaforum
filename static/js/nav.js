let navBurger = document.getElementsByClassName('nav-burger')[0];
let navBurgerIcon = document.getElementsByName('menu-outline')[0];
let mainNav = document.getElementsByClassName('nav-elements')[0];
navBurger.addEventListener('click', function(){
    if (window.getComputedStyle(mainNav,null).display === "none") {
        mainNav.style.display = "flex";
        navBurgerIcon.setAttribute("name","close-outline")
    } else {
        mainNav.style.display = "none"
        navBurgerIcon.setAttribute("name","menu-outline")
    }
})