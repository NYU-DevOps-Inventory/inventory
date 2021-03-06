$(function () {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

  // Updates the form with data from the response
  function update_form_data(res) {
    $('#inventory_product_id').val(res.product_id);
    if (res.condition == 'NEW') {
      $('#inventory_condition').val('NEW');
    } else if (res.condition == 'OPEN BOX') {
      $('#inventory_condition').val('OPEN BOX');
    } else {
      //'USED'
      $('#inventory_condition').val('USED');
    }
    $('#inventory_quantity').val(res.quantity);
    $('#inventory_restock_level').val(res.restock_level);
    if (res.available == true) {
      $('#inventory_available').val('true');
    } else {
      $('#inventory_available').val('false');
    }
  }

  // Clears all form fields
  function clear_form_data() {
    $('#inventory_restock_level').val('');
    $('#inventory_quantity').val('');
    $('#inventory_quantity_low').val('');
    $('#inventory_quantity_high').val('');
    $('#inventory_add_amount').val('');
  }

  // Updates the flash message area
  function flash_message(message) {
    $('#flash_message').empty();
    $('#flash_message').append(message);
  }

  // ****************************************
  // Create an Inventory
  // ****************************************

  $('#create-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();
    var quantity = $('#inventory_quantity').val();
    var restock_level = $('#inventory_restock_level').val();
    var available = $('#inventory_available').val() == 'true';

    // Convert input type
    if (!isNaN(quantity)) {
      quantity = parseInt(quantity);
    }
    if (!isNaN(restock_level)) {
      restock_level = parseInt(restock_level);
    }

    var data = {
      product_id: product_id,
      condition: condition,
      quantity: quantity,
      restock_level: restock_level,
      available: available,
    };

    var ajax = $.ajax({
      type: 'POST',
      url: '/api/inventory',
      contentType: 'application/json',
      data: JSON.stringify(data),
    });

    ajax.done(function (res) {
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Update an Inventory
  // ****************************************

  $('#update-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();
    var restock_level = $('#inventory_restock_level').val();
    var quantity = $('#inventory_quantity').val();

    // Convert input type
    if (!isNaN(quantity)) {
      quantity = parseInt(quantity);
    }
    if (!isNaN(restock_level)) {
      restock_level = parseInt(restock_level);
    }

    var data = {
      quantity: quantity,
      restock_level: restock_level
    };

    var ajax = $.ajax({
      type: 'PUT',
      url: '/api/inventory/' + product_id + '/condition/' + condition,
      contentType: 'application/json',
      data: JSON.stringify(data),
    });

    ajax.done(function (res) {
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Retrieve an Inventory
  // ****************************************

  $('#retrieve-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();

    var ajax = $.ajax({
      type: 'GET',
      url: '/api/inventory/' + product_id + '/condition/' + condition,
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      clear_form_data();
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Delete an Inventory
  // ****************************************

  $('#delete-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();

    var ajax = $.ajax({
      type: 'DELETE',
      url: '/api/inventory/' + product_id + '/condition/' + condition,
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      clear_form_data();
      flash_message('Inventory has been Deleted!');
    });

    ajax.fail(function (res) {
      flash_message('Server error!');
    });
  });

  // ****************************************
  // Activate an Inventory
  // ****************************************

  $('#activate-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();

    var ajax = $.ajax({
      type: 'PUT',
      url: '/api/inventory/' + product_id + '/condition/' + condition + '/activate',
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      clear_form_data();
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Deactivate an Inventory
  // ****************************************

  $('#deactivate-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();

    var ajax = $.ajax({
      type: 'PUT',
      url:
        '/api/inventory/' + product_id + '/condition/' + condition + '/deactivate',
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      clear_form_data();
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Add amount to an Inventory
  // ****************************************

  $('#add-amount-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();
    var add_amount = $('#inventory_add_amount').val();

    // Convert input type
    if (!isNaN(add_amount)) {
      add_amount = parseInt(add_amount);
    }

    var data = {
      quantity: add_amount
    };

    var ajax = $.ajax({
      type: 'PUT',
      url: '/api/inventory/' + product_id + '/condition/' + condition + '?added_amount=True',
      contentType: 'application/json',
      data: JSON.stringify(data),
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      clear_form_data();
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Clear the form
  // ****************************************

  $('#clear-btn').click(function () {
    $('#inventory_product_id').val('');
    clear_form_data();
  });

  // ****************************************
  // Search for an Inventory
  // ****************************************

  $('#search-btn').click(function () {
    var product_id = $('#inventory_product_id').val();
    var condition = $('#inventory_condition').val();
    var quantity = $('#inventory_quantity').val();
    var quantity_low = $('#inventory_quantity_low').val();
    var quantity_high = $('#inventory_quantity_high').val();
    var restock_level = $('#inventory_restock_level').val();
    var available = $('#inventory_available').val() == 'true';

    var queryString = '';

    // TODO: Refactor these if else block
    if (product_id) {
      queryString += 'product_id=' + product_id;
    }
    if (condition) {
      if (queryString.length > 0) {
        queryString += '&condition=' + condition;
      } else {
        queryString += 'condition=' + condition;
      }
    }
    if (quantity) {
      if (queryString.length > 0) {
        queryString += '&quantity=' + quantity;
      } else {
        queryString += 'quantity=' + quantity;
      }
    }
    if (restock_level) {
      if (queryString.length > 0) {
        queryString += '&restock_level=' + restock_level;
      } else {
        queryString += 'restock_level=' + restock_level;
      }
    }
    if (quantity_low) {
      if (queryString.length > 0) {
        queryString += '&quantity_low=' + quantity_low;
      } else {
        queryString += 'quantity_low=' + quantity_low;
      }
    }
    if (quantity_high) {
      if (queryString.length > 0) {
        queryString += '&quantity_high=' + quantity_high;
      } else {
        queryString += 'quantity_high=' + quantity_high;
      }
    }
    // available
    if (queryString.length > 0) {
      queryString += '&available=' + available;
    } else {
      queryString += 'available=' + available;
    }

    var ajax = $.ajax({
      type: 'GET',
      url: '/api/inventory?' + queryString,
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      $('#search_results').empty();
      $('#search_results').append(
        '<table class="table-striped" cellpadding="10">'
      );
      var header = '<tr>';
      header += '<th style="width:10%">Product_ID</th>';
      header += '<th style="width:30%">Condition</th>';
      header += '<th style="width:30%">Quantity</th>';
      header += '<th style="width:30%">Restock Level</th>';
      header += '<th style="width:10%">Available</th></tr>';
      $('#search_results').append(header);
      var firstInventory = '';
      for (let i = 0; i < res.length; ++i) {
        var inventory = res[i];
        var row =
          '<tr><td>' +
          inventory.product_id +
          '</td><td>' +
          inventory.condition +
          '</td><td>' +
          inventory.quantity +
          '</td><td>' +
          inventory.restock_level +
          '</td><td>' +
          inventory.available +
          '</td></tr>';
        $('#search_results').append(row);
        if (i == 0) {
          firstInventory = inventory;
        }
      }

      $('#search_results').append('</table>');

      // copy the first result to the form
      if (firstInventory != '') {
        update_form_data(firstInventory);
      } else {
        $('#search_results').append('No matched results.');
      }

      flash_message('Success');
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
    });
  });
});
