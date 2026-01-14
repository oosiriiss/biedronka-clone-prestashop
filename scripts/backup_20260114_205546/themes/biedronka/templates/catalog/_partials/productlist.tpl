<div class="flex gap-1">
    {foreach from=$products item="product" key="position"}
        {include file="catalog/_partials/miniatures/product.tpl" product=$product position=$position }
    {/foreach}
</div>
