$(function () {

    /*
     * Primero ocultamos los submenús
     */
    $(".submenu").hide();

    /*
     * Detectamos la vista actual
     */
    const rutaActual = window.location.pathname.replace(/\/$/, "");

    $(".menu-link").each(function () {
        const $enlace = $(this);
        const urlEnlace = new URL(this.href, window.location.origin);
        const rutaEnlace = urlEnlace.pathname.replace(/\/$/, "");

        if (rutaActual.includes(rutaEnlace)) {

            /*
             * Marcamos el hijo actual
             */
            $enlace.addClass("active");

            /*
             * Abrimos todos sus padres
             */
            $enlace.parents(".submenu").each(function () {
                const $submenu = $(this);
                const $menuItem = $submenu.closest(".menu-item");
                const $boton = $menuItem.children(".menu-toggle");

                // Muestra el submenú que contiene al hijo activo
                $submenu.show();

                // Mantiene abierto el padre
                $boton.attr("aria-expanded", "true");
                $boton.find(".arrow").text("▾");
                $boton.addClass("parent-active");
            });
        }
    });


    /*
     * Abrir y cerrar menús manualmente
     */
    $(document).on("click", ".menu-toggle", function (event) {
        event.preventDefault();
        event.stopPropagation();

        const $boton = $(this);
        const $menuItem = $boton.closest(".menu-item");
        const $submenu = $menuItem.children(".submenu");

        const abierto = $boton.attr("aria-expanded") === "true";

        if (abierto) {
            $submenu.stop(true, true).slideUp(250);
            $boton.attr("aria-expanded", "false");
            $boton.find(".arrow").text("▸");
        } else {
            $submenu.stop(true, true).slideDown(250);
            $boton.attr("aria-expanded", "true");
            $boton.find(".arrow").text("▾");
        }
    });

    
    const $link = $(".btnSpiner");

    if (!$link.length) {
        return;
    }

    $link.on("click", function (event) {
        const $this = $(this);
        const $spinner = $this.find(".spinner-border");
        const $text = $this.find(".link-text");

        $spinner.removeClass("d-none");
        $text.text("Cargando...");

        $this.addClass("disabled");
        $this.attr("aria-disabled", "true");
        $this.css("pointer-events", "none");
    });

});
