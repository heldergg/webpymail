/*
 * Menu
 */

/* config */
var visible = false;

/* Menu functions */

function setup_menu(menu_items) {
    var menu_toggle = menu_items + '_toggle';
    $(menu_items).hide();

    $(menu_toggle).click( function() {
        if (visible) {
            $(menu_items).hide();
            $("#menu_back").hide();
            visible = false;
        } else {
            $("#menu_back").show();
            $(menu_items).show();
            visible = true;
        };
    });

    $("#menu_back").click( function() {
        $(menu_items).hide();
        $("#menu_back").hide();
        visible = false;
    });
};

/* Initialization */

$(function() {
    setup_menu("#main_menu");
    setup_menu("#filter_menu");
    setup_menu("#tools_menu");
});



