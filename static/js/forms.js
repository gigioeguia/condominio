$(function () {
    // sourcery skip: avoid-function-declarations-in-blocks
    function initializeRemoteSelect(selector, defaultValue = null, param=null) {
        const select = $(selector);

        if (!select.length) {
            return;
        }

        const apiUrl = select.data("url");

        if (!apiUrl) {
            console.error(`No se encontró data-url para ${selector}`);
            return;
        }

        const dataParam = JSON.stringify(param);


        select.select2({
            width: "100%",
            placeholder: select.data("placeholder"),
            allowClear: true,
            minimumInputLength: 0,
            ajax: {
                url: apiUrl,
                dataType: "json",
                delay: 300,

                data: function (params) {
                    return {
                        term: params.term || "", 
                        dataParam
                    };
                },

                processResults: function (data) {
                    return {
                        results: data.results || []
                    };
                },

                cache: true
            }
        });

        const currentValue = select.val() || defaultValue;

        if (!currentValue) {
            return;
        }

        if (
            select.find("option[value='" + currentValue + "']").length === 0
        ) {
            const option = new Option(
                currentValue,
                currentValue,
                true,
                true
            );

            select.append(option);
        }

        select.val(currentValue).trigger("change");
    }

    const currencySelect= $("#id_country");
    initializeRemoteSelect( "#id_default_currency", currencySelect );
 
    const countrySelect = $("#id_country");
    initializeRemoteSelect("#id_country",countrySelect);

    const chartOfAccountsSelect = $("#id_chart_of_accounts")
    initializeRemoteSelect("#id_chart_of_accounts",chartOfAccountsSelect,{ "country": countrySelect.val() });

    countrySelect.on("change", function () {
        const selectedText = countrySelect.find("option:selected").text();
        initializeRemoteSelect("#id_chart_of_accounts",chartOfAccountsSelect,{ "country": selectedText });
        $("#id_chart_of_accounts").val(null).trigger("change");
    });

});
