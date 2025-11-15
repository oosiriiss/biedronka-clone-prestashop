
{**{extends file='parent:_partials/header.tpl'}*}


{**category items*}
{assign var='categories' value=[]}

{append var='items' value=['title' => 'Polecane', 'icon' => 'TODO']} 
{append var='items' value=['title' => 'Warzywa', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Owoce', 'icon' => 'TODO']} 
{append var='items' value=['title' => 'Piekarnia', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Nabiał', 'icon' => 'TODO']} 
{append var='items' value=['title' => 'Mięso', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Dania gotowe', 'icon' => 'TODO']} 
{append var='items' value=['title' => 'Napoje', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Mrożone', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Artykuły spożywcze', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Drogeria', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Dla domu', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Dla dzieci', 'icon' => 'TODO']}
{append var='items' value=['title' => 'Dla zwierząt', 'icon' => 'TODO']}

<div id="nav-wrapper"class="flex items-center shadow-md py-1 px-6">
   <span class="font-black text-3xl text-red-500 grow-1">
      Szpontonka
   </span>
   
   <div class="flex items-center content-center gap-4">

      <div class="h-min">
	 {hook h='displaySearch'}
      </div>

      <div class="card-soft rounded-lg text-xs font-bold">
	 {** TODO :: Icon *}
	 Dodaj adres dostawy
      </div>

      <div class="card-soft rounded-lg text-xs font-bold">
	 {** TODO :: Icon *}
	 Termin dostawy
      </div>

      <div class="h-min">
	 {hook h='displayLogin'}
      </div>

      <div class="h-min">
	 {hook h='displayCart'}
      </div>

   </div>
</div>
   
<div>
   {** Categry menu for large screens*}
   <div class="hidden xl:flex gap-2">
      {foreach $items as $item}
         <div class="flex flex-col grow-1 content-center items-center text-center text-xs text-neutral-700 font-bold">
         	 {$item.icon}
   	 {$item.title}
         </div>
      {/foreach}
   </div>

   {** Categry menu mobile *}
   <div id="mobile_menu_closed_placeholder" class="xl:hidden">
      <label for="mobile_menu_close" class="cursor-pointer">
         <input type="checkbox" id="mobile_menu_close" class="hidden"/>
         <div class="block space-y-1 p-1">
            <div class="h-1 w-6 bg-black"></div>
            <div class="h-1 w-6 bg-black"></div>
            <div class="h-1 w-6 bg-black"></div>
         </div>
      </div>
   </div>

   <div class="flex absolute top-0 left-0 h-screen xl:hidden">
      <div id="mobile_menu" class="transition-all max-w-0 overflow-clip bg-white ">
	 <div class="p-2">
      	    <div class="font-bold text-lg text-black mb-4">Wszystkie kategorie</div>
	    <div class="space-y-4">
	     {foreach $items as $item}
      	        <div class="flex card-soft rounded-lg">
      	           <div class="gap-2 grow-1">
      	        	 {$item.icon}
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
      <div id="mobile_menu_open_placeholder">
      </div>
   </div>
</div>


{** Original template for reference *}
{include file='parent:_partials/header.tpl'}

