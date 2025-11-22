console.log("nice");




function toggleNavigationDrawer(drawer,closeButton,checkbox,openedPlaceholder,closedPlaceholder) {

    drawer.classList.toggle("open");

    const isOpening = drawer.classList.contains("open");

    checkbox.checked = isOpening;

    if(isOpening) {
        // mobileMenu.classList.replace('max-w-0','max-w-2xl');
        openedPlaceholder.appendChild(closeButton);
    } else {
        // mobileMenu.classList.replace('max-w-2xl','max-w-0');
        closedPlaceholder.appendChild(closeButton);
    }
}

document.addEventListener('DOMContentLoaded', (e) => {
   const mobileMenu = document.getElementById("mobile_menu");
   const closedPlaceholder = document.getElementById("mobile_menu_closed_placeholder");
   const openedPlaceholder = document.getElementById("mobile_menu_open_placeholder");
   const checkBox = document.getElementById("mobile_menu_close");
   const closeButton = checkBox.parentNode;

   closeButton.addEventListener('change', (e) => {
       toggleNavigationDrawer(mobileMenu,closeButton,checkBox,openedPlaceholder,closedPlaceholder);
   });

    const backgroundDim = document.getElementById("nav_drawer_dim");

    backgroundDim.addEventListener('click', e =>{
        toggleNavigationDrawer(mobileMenu,closeButton,checkBox,openedPlaceholder,closedPlaceholder);
    });
})
