<div class="mr-2 last:mr-0 max-w-[168px] md:max-w-[272px] md+:max-w-[308px] w-full bg-white rounded-br-4xl border border-gray-200 shadow-sm relative overflow-hidden group">

    <button aria-label="favorite" class="hidden group-hover:block absolute top-3 right-3 text-red-500 z-10">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
             class="stroke-current">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z"
                  stroke="currentColor" stroke-width="1.4" fill="transparent" stroke-linecap="round"
                  stroke-linejoin="round"/>
        </svg>
    </button>

    <div class="relative max-h-min flex items-start m-4">
        <div class="w-28 h-28 flex items-center justify-center">
            {if $product.cover}
                <a href="{$product.url}" class="thumbnail product-thumbnail">
                    <img
                            src="{$product.cover.bySize.home_default.url}"
                            alt="{if !empty($product.cover.legend)}{$product.cover.legend}{else}{$product.name|truncate:30:'...'}{/if}"
                            loading="lazy"
                            data-full-size-image-url="{$product.cover.large.url}"
                            width="{$product.cover.bySize.home_default.width}"
                            height="{$product.cover.bySize.home_default.height}"
                    />
                </a>
            {else}
                <a href="{$product.url}" class="thumbnail product-thumbnail">
                    <img
                            src="{$urls.no_picture_image.bySize.home_default.url}"
                            loading="lazy"
                            width="{$urls.no_picture_image.bySize.home_default.width}"
                            height="{$urls.no_picture_image.bySize.home_default.height}"
                    />
                </a>
            {/if}
        </div>


        <div class="absolute bottom-0 right-0 flex flex-col">
            {if $product.has_discount}
                {if $product.discount_type === 'percentage'}
                    <span class="rounded-t-sm bg-yellow-300 font-bold py-[2px] text-xs text-center">
                    {$product.discount_percentage}
                </span>
                {elseif $product.discount_type === 'amount'}
                    <span class="rounded-t-sm bg-yellow-300 font-bold py-[2px] text-xs text-center">
                    {$product.discount_amount_to_display}
                </span>
                {/if}
            {/if}
            <div class="bg-red-600 text-white
            rounded-b-sm  {if !$product.has_discount}rounded-t-sm{/if}
            shadow-lg flex px-[12px] py-[6px] font-bold gap-0.5">
                <div class="text-2xl leading-none">89</div>
                <div class="flex flex-col">
                    <span class="text-xs leading-none">99</span>
                    <span class="text-xs leading-none">/szt</span>
                </div>
            </div>
        </div>
    </div>

    <div class="px-5 min-h-40">
        <h3 class="text-sm! font-semibold text-gray-900">
            {$product.name|truncate:30}
        </h3>
        <p class="text-[10px]! text-gray-500">
            1kg - 89,99 zł / kg
        </p>
    </div>

    <button aria-label="add"
            class="absolute right-3 bottom-3 w-10 h-10 bg-white  text-red-500 border-red-500 border-1 rounded-full text-5xl flex items-center justify-center">
        +
    </button>
</div>

{*{block name='product_miniature_item'}*}
{*    <div class="js-product product{if !empty($productClasses)} {$productClasses}{/if}">*}
{*        <article class="product-miniature js-product-miniature" data-id-product="{$product.id_product}" data-id-product-attribute="{$product.id_product_attribute}">*}
{*            <div class="thumbnail-container">*}
{*                <div class="thumbnail-top">*}
{*                    {block name='product_thumbnail'}*}
{*                        {if $product.cover}*}
{*                            <a href="{$product.url}" class="thumbnail product-thumbnail">*}
{*                                <img*}
{*                                        src="{$product.cover.bySize.home_default.url}"*}
{*                                        alt="{if !empty($product.cover.legend)}{$product.cover.legend}{else}{$product.name|truncate:30:'...'}{/if}"*}
{*                                        loading="lazy"*}
{*                                        data-full-size-image-url="{$product.cover.large.url}"*}
{*                                        width="{$product.cover.bySize.home_default.width}"*}
{*                                        height="{$product.cover.bySize.home_default.height}"*}
{*                                />*}
{*                            </a>*}
{*                        {else}*}
{*                            <a href="{$product.url}" class="thumbnail product-thumbnail">*}
{*                                <img*}
{*                                        src="{$urls.no_picture_image.bySize.home_default.url}"*}
{*                                        loading="lazy"*}
{*                                        width="{$urls.no_picture_image.bySize.home_default.width}"*}
{*                                        height="{$urls.no_picture_image.bySize.home_default.height}"*}
{*                                />*}
{*                            </a>*}
{*                        {/if}*}
{*                    {/block}*}

{*                    <div class="highlighted-informations{if !$product.main_variants} no-variants{/if}">*}
{*                        {block name='quick_view'}*}
{*                            <a class="quick-view js-quick-view" href="#" data-link-action="quickview">*}
{*                                <i class="material-icons search">&#xE8B6;</i> {l s='Quick view' d='Shop.Theme.Actions'}*}
{*                            </a>*}
{*                        {/block}*}

{*                        {block name='product_variants'}*}
{*                            {if $product.main_variants}*}
{*                                {include file='catalog/_partials/variant-links.tpl' variants=$product.main_variants}*}
{*                            {/if}*}
{*                        {/block}*}
{*                    </div>*}
{*                </div>*}

{*                <div class="product-description">*}
{*                    {block name='product_name'}*}
{*                        {if $page.page_name == 'index'}*}
{*                            <h3 class="h3 product-title"><a href="{$product.url}" content="{$product.url}">{$product.name|truncate:30:'...'}</a></h3>*}
{*                        {else}*}
{*                            <h2 class="h3 product-title"><a href="{$product.url}" content="{$product.url}">{$product.name|truncate:30:'...'}</a></h2>*}
{*                        {/if}*}
{*                    {/block}*}

{*                    {block name='product_price_and_shipping'}*}
{*                        {if $product.show_price}*}
{*                            <div class="product-price-and-shipping">*}
{*                                {if $product.has_discount}*}
{*                                    {hook h='displayProductPriceBlock' product=$product type="old_price"}*}

{*                                    <span class="regular-price" aria-label="{l s='Regular price' d='Shop.Theme.Catalog'}">{$product.regular_price}</span>*}
{*                                    {if $product.discount_type === 'percentage'}*}
{*                                        <span class="discount-percentage discount-product">{$product.discount_percentage}</span>*}
{*                                    {elseif $product.discount_type === 'amount'}*}
{*                                        <span class="discount-amount discount-product">{$product.discount_amount_to_display}</span>*}
{*                                    {/if}*}
{*                                {/if}*}

{*                                {hook h='displayProductPriceBlock' product=$product type="before_price"}*}

{*                                <span class="price" aria-label="{l s='Price' d='Shop.Theme.Catalog'}">*}
{*                {capture name='custom_price'}{hook h='displayProductPriceBlock' product=$product type='custom_price' hook_origin='products_list'}{/capture}*}
{*                                    {if '' !== $smarty.capture.custom_price}*}
{*                                        {$smarty.capture.custom_price nofilter}*}
{*                                    {else}*}
{*                                        {$product.price}*}
{*                                    {/if}*}
{*              </span>*}

{*                                {hook h='displayProductPriceBlock' product=$product type='unit_price'}*}

{*                                {hook h='displayProductPriceBlock' product=$product type='weight'}*}
{*                            </div>*}
{*                        {/if}*}
{*                    {/block}*}

{*                    {block name='product_reviews'}*}
{*                        {hook h='displayProductListReviews' product=$product}*}
{*                    {/block}*}
{*                </div>*}

{*                {include file='catalog/_partials/product-flags.tpl'}*}
{*            </div>*}
{*        </article>*}
{*    </div>*}
{*{/block}*}
