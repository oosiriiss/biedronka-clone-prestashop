Fakture trzeba wystawic recznie w panelu admina i potem zmienic status zamowienia zeby byla widoczna u uzytkownika.

Potem podmenic dane logowania "EMAIL" i "PASSWORD" w pliku faktura.py na uzytkownika kotry zlozyl zamowienie

Jesli byly by jakiesbledy z sslem to trzeba to wkleic na koniec pliku do 'config/defines.inc.php' w kontenerze prestashopa

$default_opts = array(
    'ssl' => array(
        'verify_peer' => false,
        'verify_peer_name' => false,
    )
);
stream_context_set_default($default_opts);
