// ===== Alzheimer Care System - Main JS =====
$(document).ready(function() {

    // Auto-hide messages after 4 seconds
    setTimeout(function() {
        $('.alert-dismissible').fadeOut('slow');
    }, 4500);

    // Role selector in login
    $('.role-selector label').on('click', function() {
        $('.role-selector label').removeClass('active');
        $(this).addClass('active');
        $(this).siblings('input[type="radio"]').prop('checked', true);
        var input = $('input[name="role"][value="' + $(this).data('role') + '"]');
        input.prop('checked', true);
    });

    // Sidebar toggle (mobile)
    $('#sidebarToggle').on('click', function() {
        $('.sidebar').toggleClass('open');
    });

    // Confirm delete
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });

    // Mark medicine as taken (AJAX)
    $('.mark-taken-btn').on('click', function(e) {
        e.preventDefault();
        var btn = $(this);
        var url = btn.data('url');
        $.ajax({
            url: url,
            type: 'GET',
            success: function(resp) {
                btn.removeClass('btn-primary').addClass('btn-success').html('<i class="bi bi-check2"></i> Taken');
                showToast(resp.message || 'Marked as taken', 'success');
            },
            error: function() {
                showToast('Failed to mark as taken', 'danger');
            }
        });
    });

    // Toast helper
    window.showToast = function(message, type) {
        type = type || 'info';
        var toast = $('<div class="alert alert-' + type + ' alert-dismissible toast-msg" style="position:fixed;top:20px;right:20px;z-index:9999;min-width:280px;box-shadow:0 4px 20px rgba(0,0,0,0.15);">' + message + '</div>');
        $('body').append(toast);
        setTimeout(function() { toast.fadeOut(400, function() { $(this).remove(); }); }, 3500);
    };

    // Live search filter on tables (data-filter attribute)
    $('[data-filter-target]').on('keyup', function() {
        var target = $(this).data('filter-target');
        var val = $(this).val().toLowerCase();
        $(target + ' tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(val) > -1);
        });
    });
});
