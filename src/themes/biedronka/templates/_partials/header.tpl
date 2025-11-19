
{**{extends file='parent:_partials/header.tpl'}*}


{**category items*}
{assign var='categories' value=[]}

{**Icons' path relative to the theme's assets/img directory*}
{append var='items' value=['title' => 'Polecane', 'icon' => 'biedronka.webp']} 
{append var='items' value=['title' => 'Warzywa', 'icon' => 'broccoli.webp']}
{append var='items' value=['title' => 'Owoce', 'icon' => 'banana.webp']} 
{append var='items' value=['title' => 'Piekarnia', 'icon' => 'bun.png']}
{append var='items' value=['title' => 'Nabiał', 'icon' => 'dairy.webp']} 
{append var='items' value=['title' => 'Mięso', 'icon' => 'meat.webp']}
{append var='items' value=['title' => 'Dania gotowe', 'icon' => 'dumpling.webp']} 
{append var='items' value=['title' => 'Napoje', 'icon' => 'drinks.webp']}
{append var='items' value=['title' => 'Mrożone', 'icon' => 'snowflake.webp']}
{append var='items' value=['title' => 'Artykuły spożywcze', 'icon' => 'olive-jar.webp']}
{append var='items' value=['title' => 'Drogeria', 'icon' => 'cosmetics.webp']}
{append var='items' value=['title' => 'Dla domu', 'icon' => 'cleaning.webp']}
{append var='items' value=['title' => 'Dla dzieci', 'icon' => 'kids.webp']}
{append var='items' value=['title' => 'Dla zwierząt', 'icon' => 'animals.webp']}



<div class="max-w-7xl mx-auto py-2 mx-auto flex items-center justify-between xl:justify-start">
   <img src="{$urls.theme_assets}img/storefront-logo.svg" >

   <div class="hidden xl:block w-full">
      {include file="_partials/header-search-delivery.tpl"}
   </div>

   <div class="flex gap-4">
      <div class="h-min">
   	    {hook h='displayLogin'}
   	 </div>

   	 <div class="h-min">
   	    {hook h='displayCart'}
   	 </div>

   </div>

</div>



{** divider *}
<div class="h-1 w-[100vw] shadow-xs">
</div>
   
<div class="flex flex-row max-w-7xl mx-auto items-center">

   {** Categry menu for large screens*}
   <div class="hidden xl:flex gap-2 py-1 w-full">
      {foreach $items as $item}
         <div class="flex flex-col gap-2 grow-1 content-center items-center text-center text-xs text-neutral-700 font-bold">
            <img src="{$urls.theme_assets}img/{$item.icon}"
	            class="w-[24px] h-[24px]"
	       >	
            {$item.title}
         </div>
      {/foreach}
   </div>

   {** Categry menu mobile *}
   <div id="mobile_menu_closed_placeholder" class="xl:hidden">
      <label for="mobile_menu_close" class="cursor-pointer flex flex-col p-1 items-center content-center m-0">
	  <input type="checkbox" id="mobile_menu_close" class="hidden peer"/>
          <div class="mb-[3px] h-1 w-6 bg-black transition-all duration-300 ease-in-out peer-checked:translate-y-2 peer-checked:rotate-45"></div>
          <div class="mb-[3px] h-1 w-6 bg-black transition-all duration-300 ease-in-out peer-checked:opacity-0"></div>
          <div class="h-1 w-6 bg-black transition-all duration-300 ease-in-out peer-checked:-translate-y-2 peer-checked:-rotate-45"></div>
      </div>

      <div class="block xl:hidden">
   	    {include file="_partials/header-search-delivery.tpl"}
   	 </div>

   </div>


   {** Mobile drawer **}
   <div class="flex absolute top-0 left-0 h-screen xl:hidden">
      <div id="mobile_menu" class="peer-has-checked:max-w-2xl transition-all max-w-0 overflow-clip bg-white">
         <div class="p-2">
            <div class="font-bold text-lg text-black mb-4">Wszystkie kategorie</div>
     	  <div class="space-y-4">
     	     {foreach $items as $item}
      	        <div class="flex card-soft rounded-lg">
      	           <div class="gap-2 grow-1">
     		      <img src="{$urls.theme_assets}img/{$item.icon}">
     		      <span class="text-black font-bold">{$item.title}</span>
      	           </div>
      	           <div>
     		      &gt;
      	           </div>
      	        </div>
      	     {/foreach}
            </div>
         </div>
      </div>
      <div id="mobile_menu_open_placeholder" class="peer"></div>
   </div>

</div>

{** divider *}
<div class="h-1 w-[100vw] shadow-md">
</div>

