document.addEventListener("DOMContentLoaded", function () {
    let selectedInputLanguage = null;
    let selectedOutputLanguage = null;
    let selectedStartDate = null;
    let selectedEndDate = null;
    let sortOrder = 0; // デフォルト昇順
    let searchKeyword = "";
    let showFavoritesValue = "0"; // デフォルト"0"
    const totalDataCount = 100;
    const itemsPerPage = 10;


    // ドロップダウンメニュー要素の取得
    const inputLanguageDropdown = document.getElementById("inputLanguageDropdown");
    const outputLanguageDropdown = document.getElementById("outputLanguageDropdown");

    // 日付選択ボタン
    const startDate = document.getElementById("startDate");
    const endDate = document.getElementById("endDate");

    // ソートボタン要素の取得
    const ascendingOrderButton = document.getElementById("ascendingOrderButton");
    const descendingOrderButton = document.getElementById("descendingOrderButton");

    // 検索ボタンと入力フィールド要素の取得
    const searchButton = document.getElementById("searchButton");
    const searchInput = document.getElementById("searchInput");

    // いいねのリストブタン
    const showFavoritesButton = document.getElementById("showFavoritesButton");
    showFavoritesButton.addEventListener("click", function () {
        if (showFavoritesValue === "0") {
            showFavoritesValue = "1";
        } else {
            showFavoritesValue = "0";
        }
    });

    // ドロップダウンメニューのクリックイベントリスナーを追加する
    inputLanguageDropdown.addEventListener("click", function (event) {
        selectedInputLanguage = event.target.textContent;
    });

    outputLanguageDropdown.addEventListener("click", function (event) {
        selectedOutputLanguage = event.target.textContent;
    });

    // 日付選択イベントリスナーを追加する
    startDate.addEventListener("change", function (event) {
        selectedStartDate = event.target.value;
    });

    endDate.addEventListener("change", function (event) {
        selectedEndDate = event.target.value;
    });

    // ソートボタンのクリックイベントリスナーを追加する
    ascendingOrderButton.addEventListener("click", function () {
        sortOrder = 0; // 0 は昇順
    });

    descendingOrderButton.addEventListener("click", function () {
        sortOrder = 1; // 1 は降順
    });

    //検索ボタンのクリックイベントリスナーを追加する
    searchButton.addEventListener("click", function () {
        searchKeyword = searchInput.value;
    });

    //リセットボタンの機能
    const resetButton = document.getElementById("resetButton");

    //リセットボタンのクリックイベントリスナーを追加する
    resetButton.addEventListener("click", function () {
        // すべてのオプションをデフォルトの状態に戻す
        selectedInputLanguage = null;
        selectedOutputLanguage = null;
        selectedStartDate = null;
        selectedEndDate = null;
        sortOrder = 0; // 昇順に戻す
        showFavoritesValue = "0"; // 非表示に戻す
        searchKeyword = ""; // 検索キーワードをデフォルトに戻す

        // ドロップダウンメニューの選択をクリアする
        inputLanguageDropdown.querySelectorAll("a").forEach((item) => {
            item.classList.remove("selected");
        });
        outputLanguageDropdown.querySelectorAll("a").forEach((item) => {
            item.classList.remove("selected");
        });
        // ひづけの選択をクリアする
        startDate.value = "";
        endDate.value = "";

        // ソートブタンの状態に戻す
        ascendingOrderButton.classList.remove("selected");
        descendingOrderButton.classList.remove("selected");
        // 検索入力欄をクリアする
        searchInput.value = searchKeyword;
        showFavoritesButton.value = "0";
    });

    const submitButton = document.getElementById("submitButton");

    // まず、ドキュメントが完全に読み込まれていることを確認してください
    document.addEventListener('DOMContentLoaded', function () {

        // ユーザーが入力言語を選択した後に発生するイベントハンドラ
        document.getElementById('inputLanguageSelect').addEventListener('change', function () {
            const selectedInputLanguage = this.value; // ユーザーが選択した入力言語を取得する
            const inputLanguageId = languageMapping[selectedInputLanguage]; // 数値にマッピングする
        });

        document.getElementById('outputLanguageSelect').addEventListener('change', function () {
            const selectedOutputLanguage = this.value;
            const outputLanguageId = languageMapping[selectedOutputLanguage];
        });
    });

    submitButton.addEventListener("click", function () {
        // データオブジェクトの構築
        const requestData = {
            input_language: languageMapping[selectedInputLanguage],
            output_language: languageMapping[selectedOutputLanguage],
            start_date: selectedStartDate,
            end_date: selectedEndDate,
            sort_order: sortOrder,
            favoritesValue: showFavoritesValue,
            search_keyword: searchKeyword,
        };

        // fetch を使用してデータオブジェクトをバックエンドに送信する
        fetch("/user_translate_history", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
        })
            .then((response) => {
                // ここでバックエンドのレスポンスを処理する
                if (response.status === 200) {
                    return response.json();
                }
            })
            .then((data) => {
                // ここでバックエンドから取得したデータを処理する
                //console.log(data)
                if (data.data_list !== null) {
                    // console.log("数据列表:", data.data_list);
                    updateTableWithData(data.data_list, data.total_pages, data.current_page);
                    updatePagination(data.total_pages, data.current_page);
                } else {
                    console.log("有効なデータリストが見つかりませんでした。");
                }
            })


    });

    function updateTableWithData(dataList, totalPages, currentPage) {
        const tableBody = document.querySelector("table tbody");
        tableBody.innerHTML = "";  // 表の内容をクリアする

        dataList.forEach((item, index) => {
            const tableRow = document.createElement("tr");
            tableRow.className = index % 2 === 0 ? "success" : "active";
            const columnsToShow = [0, 1, 2, 3];
            columnsToShow.forEach(colIndex => {
                const tableData = document.createElement("td");
                tableData.textContent = item[colIndex];
                tableRow.appendChild(tableData);
            });

            // 操作列を追加する
            const operationCell = document.createElement("td");
            const btnContainer = document.createElement("div");
            btnContainer.className = "btn-container";

            const updateForm = document.createElement("form");
            updateForm.method = "POST";
            updateForm.action = "/update_translation_item";
            let updateButton = createButton("🤍", "btn btn-primary btn-xs");
            console.log(item[4]);
            if (item[4] == 0) {
                updateButton = createButton("🤍", "btn btn-primary btn-xs");
            } else if (item[4] == 1) {
                updateButton = createButton("♥いいね♥", "btn btn-primary btn-xs");
            }

            const deleteForm = document.createElement("form");
            deleteForm.method = "POST";
            deleteForm.action = "/delete_translation_list";
            const deleteButton = createButton("削除", "btn btn-danger btn-xs");

            const hiddenInput = document.createElement("input");
            hiddenInput.type = "hidden";
            hiddenInput.name = "nid";
            hiddenInput.value = item[0];

            updateForm.appendChild(hiddenInput);
            deleteForm.appendChild(hiddenInput.cloneNode());

            btnContainer.appendChild(updateForm);
            btnContainer.appendChild(deleteForm);
            btnContainer.appendChild(updateButton);
            btnContainer.appendChild(deleteButton);

            operationCell.appendChild(btnContainer);
            tableRow.appendChild(operationCell);

            tableBody.appendChild(tableRow);
        });

        updatePagination(totalPages, currentPage);
    }

    // ボタン要素を作成するための新しい関数を追加
    function createButton(text, className) {
        const button = document.createElement("button");
        button.type = "submit";
        button.className = className;
        button.textContent = text;
        return button;
    }

    const tableBody = document.querySelector("table tbody");
    tableBody.addEventListener("click", function (event) {
        const target = event.target;
        if (target.tagName === "BUTTON") {
            const row = target.closest("tr"); // 現在の行を取得する
            const itemId = row.querySelector("input[name='nid']").value; // 行のIDを取得する
            console.log("id是" + itemId);

            if (target.classList.contains("btn-primary")) {
                if (target.textContent === "♥いいね♥") {
                    // すでに表示されている ♥いいね♥、テキストを ♥ に変更
                    target.textContent = "🤍";
                    sendFavToBackend(itemId, 0);
                } else {
                    target.textContent = "♥いいね♥";
                    sendFavToBackend(itemId, 1);
                }
            } else if (target.classList.contains("btn-danger")) {
                row.remove();
                //バックエンドに削除リクエストを送信する
                sendDeleteRequest(itemId);
            }
        }
    });

//ファヴの値をバックエンドに送信するための新しい関数を追加
    function sendFavToBackend(itemId, favValue) {
        fetch("/mark_item_updated", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({id: itemId, fav: favValue}),
        })
            .then(response => {
                if (response.status === 200) {
                    console.log("fav 値が更新されました");
                }
            })
            .catch(error => {
                console.error("エラー:", error);
            });
    }


    function sendDeleteRequest(itemId) {
        fetch("/delete_item", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({id: itemId}),
        })
            .then(response => {
                if (response.status === 200) {
                    console.log("行削除させました。");
                }
            })
            .catch(error => {
                console.error("エラー:", error);
            });
    }


    function updatePagination(totalPages, currentPage) {
        const pagination = document.getElementById("pagination");
        pagination.innerHTML = "";
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = i === currentPage ? "active" : "";
            const link = document.createElement("a");
            link.href = "#";
            link.textContent = i;
            link.addEventListener("click", () => handlePageClick(i));

            li.appendChild(link);
            pagination.appendChild(li);
        }
    }

    // ページボタンのクリックイベントを処理するための新しい関数を追加
    function handlePageClick(pageNumber) {

        console.log("Clicked on page", pageNumber);
        const requestData = {
            input_language: selectedInputLanguage,
            output_language: selectedOutputLanguage,
            start_date: selectedStartDate,
            end_date: selectedEndDate,
            sort_order: sortOrder,
            favoritesValue: showFavoritesValue,
            search_keyword: searchKeyword,
            page: pageNumber,
        };

        fetch("/user_translate_history", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
        })
            .then((response) => {
                if (response.status === 200) {
                    return response.json();
                }
            })
            .then((data) => {
                if (data.data_list !== null) {
                    console.log("データリスト:", data.data_list);
                    updateTableWithData(data.data_list, data.total_pages, data.current_page);
                } else {
                    console.log("有効なデータリストが見つかりませんでした");
                }
            })
    }
});

