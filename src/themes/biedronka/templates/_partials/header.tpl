
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


<div class="max-w-7xl mx-auto px-2 pt-2 pb-1 gap-4 flex items-center justify-between">
    <img src="{$urls.theme_assets}img/storefront-logo.svg" alt="Logo">

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
<div class="h-1 w-[100vw] shadow-xs"></div>

<div class="flex flex-row max-w-7xl mx-auto items-center">

    {** Categry menu for large screens*}
    <div class="hidden xl:flex gap-2 px-2 py-1 w-full">
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
    <div class="xl:hidden flex items-center w-full  px-2 py-1 gap-4 ">
        <div id="mobile_menu_closed_placeholder">
            <label for="mobile_menu_close" class="cursor-pointer flex flex-col items-center content-center m-0 z-1">
                <input type="checkbox" id="mobile_menu_close" class="hidden peer"/>
                <div class="mb-[3px] h-1 w-6 bg-black transition-all duration-300 ease-in-out peer-checked:translate-y-[7px] peer-checked:rotate-45"></div>
                <div class="mb-[3px] h-1 w-6 bg-black transition-all duration-300 ease-in-out peer-checked:opacity-0"></div>
                <div class="h-1 w-6 bg-black transition-all duration-300 ease-in-out peer-checked:translate-y-[-7px] peer-checked:-rotate-45"></div>
            </label>
        </div>
        {include file="_partials/header-search-delivery.tpl"}
    </div>


    {** Mobile drawer **}
    <div class="xl:hidden flex fixed top-0 left-0 h-screen z-50 transition-all group w-full max-w-0 has-checked:max-w-[412px]">
        <div id="nav_drawer_dim"
             class="fixed z-[-1] top-0 left-0 w-0 h-0 group-has-checked:w-screen group-has-checked:h-screen bg-black opacity-50"></div>
        <div id="mobile_menu" class="w-full z-1 transition-all overflow-hidden bg-white ">
            <p class="p-2 font-bold! text-lg text-black mb-4"> Wszystkie kategorie </p>
            <div class="space-y-4 px-2">
                {foreach $items as $item}
                    <a href="https://google.com" class="flex card-soft rounded-lg px-[16px] py-[12px] no-decoration">
                        <div class="flex gap-3 grow-1">
                            <img src="{$urls.theme_assets}img/{$item.icon}" width="24" height="24" alt="Category icon">
                            <span class="text-black font-[600] text-[14px]">{$item.title}</span>
                        </div>
                        <span>&gt;</span>
                    </a>
                {/foreach}
            </div>
        </div>
        <div id="mobile_menu_open_placeholder" class="m-1">
        </div>
    </div>

</div>

{** divider *}
<div class="h-1 w-[100vw] shadow-md">
</div>



