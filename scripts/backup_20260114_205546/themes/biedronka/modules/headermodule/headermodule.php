<?php

if(!defined('_PS_VERSION_')) {
   exit;
}

class HeaderModule extends Module
{
    public function __construct()
    {
        $this->name = 'headermodule';
        $this->tab = 'header_module';
        $this->version = '1.0.0';
        $this->author = 'oosiriiss';
        $this->need_instance = 0;
        $this->ps_versions_compliancy = [
            'min' => '8.0.0',
            'max' => '9.99.99',
        ];

        $this->bootstrap = true;

        parent::__construct();

        $this->displayName = $this->trans('Header module', [], 'Modules.HeaderModule.Admin');
        $this->description = $this->trans('Header utilities module', [], 'Modules.HeaderModule.Admin');

        $this->confirmUninstall = $this->trans('Are you sure you want to uninstall?', [], 'Modules.HeaderModule.Admin');

        if (!Configuration::get('headermodule')) {
            $this->warning = $this->trans('No name provided', [], 'Modules.Mymodule.Admin');
        }
    }

   public function install() {
      return parent::install();
   }

   public function uninstall() {
      return (
	 parent::uninstall()
	 && Configuration::deleteByName('headermodule')
      );
   }
}
