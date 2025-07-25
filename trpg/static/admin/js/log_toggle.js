function toggle_message(log_id) {
    const short_div = document.getElementById(`short_msg_${log_id}`);
    const full_div = document.getElementById(`full_msg_${log_id}`);
    const toggle_link = document.getElementById(`toggle_link_${log_id}`);

    if (full_div.style.display === 'none') {
        short_div.style.display = 'none';
        full_div.style.display = 'block';
        toggle_link.textContent = '[숨기기]';
    } else {
        short_div.style.display = 'block';
        full_div.style.display = 'none';
        toggle_link.textContent = '[전체 보기]';
    }
}
