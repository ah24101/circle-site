document.addEventListener('DOMContentLoaded', function() {
    // ハンバーガーアイコンとメニュー要素を取得
    const hamburgerIcon = document.getElementById('hamburger-icon');
    const mainMenu = document.getElementById('main-menu');

    // ハンバーガーアイコンがクリックされた時の処理
    if (hamburgerIcon && mainMenu) {
        hamburgerIcon.addEventListener('click', function() {
            // メニューの 'open' クラスをトグル（追加/削除）する
            mainMenu.classList.toggle('open');
        });

        // メニューの外側をクリックした時にメニューを閉じる処理
        document.addEventListener('click', function(event) {
            // クリックされた要素がハンバーガーアイコンでもメニュー内でもない場合
            if (!mainMenu.contains(event.target) && !hamburgerIcon.contains(event.target)) {
                // メニューが開いている場合、閉じる
                if (mainMenu.classList.contains('open')) {
                    mainMenu.classList.remove('open');
                }
            }
        });
    }
});