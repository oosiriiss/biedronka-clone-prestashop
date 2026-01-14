{** DEFAULT IMPLEMENTATION

   <div id="search_widget" class="search-widgets" data-search-controller-url="{$search_controller_url}">
     <form method="get" action="{$search_controller_url}">
       <input type="hidden" name="controller" value="search">
       <i class="material-icons search" aria-hidden="true">search</i>
       <input type="text" name="s" value="{$search_string}" placeholder="{l s='Search our catalog' d='Shop.Theme.Catalog'}" aria-label="{l s='Search' d='Shop.Theme.Catalog'}">
       <i class="material-icons clear" aria-hidden="true">clear</i>
     </form>
   </div>


*}


<div id="search_widget w-full" data-search-controller-url="{$search_controller_url}">
  <form class="relative px-[12px] py-[8px] border-3 border-red-100 hover:border-gray-300 rounded-lg transition-color duration-300 ease-in-out" 
  method="get" action="{$search_controller_url}"
      
  >
    <input type="hidden" name="controller" value="search">
    <input type="text" name="s" value="{$search_string}" placeholder="{l s='Szukaj w Szpontonce' d='Shop.Theme.Catalog'}" aria-label="{l s='Szukaj' d='Shop.Theme.Catalog'}"
      class="m-0! p-0! bg-transparent! w-full outline-0" >


   {** TODO :: Clear button should onnly appear when there are characters in input. *}
    <div class="absolute right-2 top-[50%] translate-y-[-50%] flex items-center gap-1 z-5;
">
       <label aria-hidden="true" class="m-0! p-0.75 bg-red-500 rounded-full">
	   <img src="{$urls.theme_assets}img/close.png" width="14" height="14" class=>
           <input type="reset" class="hidden">
       </label>

       <label aria-hidden="true" class="m-0! p-0.75 bg-red-500 rounded-full">
	   <img src="{$urls.theme_assets}img/search.png" width="14" height="14">
          <input type="submit" class="hidden">
       </label>
    </div>
  </form>
</div>
