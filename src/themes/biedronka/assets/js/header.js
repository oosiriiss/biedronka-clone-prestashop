console.log("nice");




document.addEventListener('DOMContentLoaded', (e) => {
   const mobileMenu = document.getElementById("mobile_menu");
   const closedPlaceholder = document.getElementById("mobile_menu_closed_placeholder");
   const openedPlaceholder = document.getElementById("mobile_menu_open_placeholder");
   const closeButton = document.getElementById("mobile_menu_close").parentNode;

   closeButton.addEventListener('click', (e) => {
      e.preventDefault()

      mobileMenu.classList.toggle("open");

      const isOpening = mobileMenu.classList.contains("open");
      console.log("is opening:", isOpening);
      console.log("closebutton: ",closeButton)

      if(isOpening) {
	 mobileMenu.classList.replace('max-w-0','max-w-2xl');
	 openedPlaceholder.appendChild(closeButton);
      } else {
	 mobileMenu.classList.replace('max-w-2xl','max-w-0');
	 closedPlaceholder.appendChild(closeButton);
      }
   });
})
