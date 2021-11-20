$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.product_id);
        $("#condition").val(res.condition);
        $("#quantity").val(res.quantity);
        $("#restock_level").val(res.restock_level);
        if (res.available == true) {
            $("#available").val("true");
        } else {
            $("#available").val("false");
        }
    }

    // Clears all form fields
    function clear_form_data() {
        $("#restock_level").val("");
        $("#quantity").val("");
        $("#quantity_low").val("");
        $("#quantity_high").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Inventory
    // ****************************************

    $("#create-btn").click(function () {
        var product_id = $("#product_id").val();
        var condition = $("#condition").val();
        var restock_level = $("#restock_level").val();
        var quantity = $("#quantity").val();
        var available = $("#available").val() == "true";

        // Convert input type
        if (!isNaN(quantity)) {
            quantity = parseInt(quantity)
        }
        if (!isNaN(restock_level)) {
            restock_level = parseInt(restock_level)
        }

        var data = {
            "product_id": product_id,
            "condition": condition,
            "quantity": quantity,
            "restock_level": restock_level,
            "available": available
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Inventory
    // ****************************************

    $("#update-btn").click(function () {

        var product_id = $("#product_id").val();
        var condition = $("#condition").val();
        var restock_level = $("#restock_level").val();
        var quantity = $("#quantity").val();
        var added_amount = $("#added_amount").val();
        var available = $("#available").val() == "true";

        // Convert input type
        if (!isNaN(quantity)) {
            quantity = parseInt(quantity)
        }
        if (!isNaN(added_amount)) {
            added_amount = parseInt(added_amount)
        }
        if (!isNaN(restock_level)) {
            restock_level = parseInt(restock_level)
        }

        var data = {
            "product_id": product_id,
            "condition": condition,
            "quantity": quantity,
            "restock_level": restock_level,
            "added_amount": added_amount,
            "available": available
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/inventory/" + product_id + "/condition/" + condition,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Inventory
    // ****************************************

    $("#retrieve-btn").click(function () {

        var product_id = $("#product_id").val();
        var condition = $("#condition").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory/" + product_id + "/condition/" + condition,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Inventory
    // ****************************************

    $("#delete-btn").click(function () {

        var product_id = $("#product_id").val();
        var condition = $("#condition").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/inventory/" + product_id + "/condition/" + condition,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Inventory has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        $("#condition").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for an Inventory
    // ****************************************

    $("#search-btn").click(function () {

        var product_id = $("#product_id").val();
        var condition = $("#condition").val();
        var quantity = $("#quantity").val();
        var quantity_low = $("#quantity_low").val();
        var quantity_high = $("#quantity_high").val();
        var restock_level = $("#restock_level").val();
        var available = $("#available").val() == "true";

        var queryString = ""

        // TODO: Refactor these if else block
        if (product_id) {
            queryString += 'product_id=' + product_id
        }
        if (condition) {
            if (queryString.length > 0) {
                queryString += '&condition=' + condition
            } else {
                queryString += 'condition=' + condition
            }
        }
        if (quantity) {
            if (queryString.length > 0) {
                queryString += '&quantity=' + quantity
            } else {
                queryString += 'quantity=' + quantity
            }
        }
        if (restock_level) {
            if (queryString.length > 0) {
                queryString += '&restock_level=' + restock_level
            } else {
                queryString += 'restock_level=' + restock_level
            }
        }
        if (quantity_low) {
            if (queryString.length > 0) {
                queryString += '&quantity_low=' + quantity_low
            } else {
                queryString += 'quantity_low=' + quantity_low
            }
        }
        if (quantity_high) {
            if (queryString.length > 0) {
                queryString += '&quantity_high=' + quantity_high
            } else {
                queryString += 'quantity_high=' + quantity_high
            }
        }
        // available
        if (queryString.length > 0) {
            queryString += '&available=' + available
        } else {
            queryString += 'available=' + available
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Product_ID</th>'
            header += '<th style="width:30%">Condition</th>'
            header += '<th style="width:30%">Quantity</th>'
            header += '<th style="width:30%">Restock Level</th>'
            header += '<th style="width:10%">Available</th></tr>'
            $("#search_results").append(header);
            var firstInventory = "";
            for (var i = 0; i < res.length; i++) {
                var inventory = res[i];
                var row = "<tr><td>" + inventory.product_id + "</td><td>" + inventory.condition + "</td><td>" + inventory.quantity + "</td><td>" + inventory.restock_level + "</td><td>" + inventory.available + "</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstInventory = inventory;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            } else {
                $("#search_results").append("No matched results.")
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

})
