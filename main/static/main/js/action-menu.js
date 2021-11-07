!function () {
    const menuList = document.getElementsByClassName("action-menu");
    for (let i = 0, l = menuList.length; i < l; ++i) {
        const menu = menuList[i];
        const button = menu.parentElement;
        button.addEventListener("click", function () {
            menu.classList.toggle("action-menu--active");
        });
    }
}();
