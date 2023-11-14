document.addEventListener("DOMContentLoaded", function () {
    // 初始化变量用于存储用户的选择
    let selectedInputLanguage = null;
    let selectedOutputLanguage = null;
    let selectedStartDate = null;
    let selectedEndDate = null;
    let sortOrder = 0; // 默认是升序
    let searchKeyword = ""; // 初始化变量
    let showFavoritesValue = "0"; // 初始化为 "0"
    // 假设这些是从后端获取的数据，根据实际情况修改
    const totalDataCount = 100; // 替换成实际的总数据量
    const itemsPerPage = 10; // 替换成实际的每页显示的数据量


    // 获取下拉菜单元素
    const inputLanguageDropdown = document.getElementById("inputLanguageDropdown");
    const outputLanguageDropdown = document.getElementById("outputLanguageDropdown");

    // 获取日期选择按钮元素
    const startDate = document.getElementById("startDate");
    const endDate = document.getElementById("endDate");

    // 获取排序按钮元素
    const ascendingOrderButton = document.getElementById("ascendingOrderButton");
    const descendingOrderButton = document.getElementById("descendingOrderButton");

    // 获取搜索按钮和输入框元素
    const searchButton = document.getElementById("searchButton");
    const searchInput = document.getElementById("searchInput");

    // 获取显示收藏按钮的值
    const showFavoritesButton = document.getElementById("showFavoritesButton");
    showFavoritesButton.addEventListener("click", function () {
        if (showFavoritesValue === "0") {
            showFavoritesValue = "1"; // 切换值，0 表示不显示，1 表示显示
        } else {
            showFavoritesValue = "0";
        }
    });

    // 添加下拉菜单点击事件监听器
    inputLanguageDropdown.addEventListener("click", function (event) {
        selectedInputLanguage = event.target.textContent;
    });

    outputLanguageDropdown.addEventListener("click", function (event) {
        selectedOutputLanguage = event.target.textContent;
    });

    // 添加日期选择事件监听器
    startDate.addEventListener("change", function (event) {
        selectedStartDate = event.target.value;
    });

    endDate.addEventListener("change", function (event) {
        selectedEndDate = event.target.value;
    });

    // 添加排序按钮点击事件监听器
    ascendingOrderButton.addEventListener("click", function () {
        sortOrder = 0; // 0 表示升序
    });

    descendingOrderButton.addEventListener("click", function () {
        sortOrder = 1; // 1 表示降序
    });

    // 添加搜索按钮点击事件监听器
    searchButton.addEventListener("click", function () {
        searchKeyword = searchInput.value;
        // 其他操作...
    });

    //重置按钮的机能
    // 获取重置按钮元素
    const resetButton = document.getElementById("resetButton");

    // 添加重置按钮点击事件监听器
    resetButton.addEventListener("click", function () {
        // 将所有选项恢复为默认状态
        selectedInputLanguage = null;
        selectedOutputLanguage = null;
        selectedStartDate = null;
        selectedEndDate = null;
        sortOrder = 0; // 恢复为升序
        showFavoritesValue = "0"; // 恢复为不显示
        searchKeyword = ""; // 恢复搜索关键词为默认值

        // 清空下拉菜单选择
        inputLanguageDropdown.querySelectorAll("a").forEach((item) => {
            item.classList.remove("selected");
        });
        outputLanguageDropdown.querySelectorAll("a").forEach((item) => {
            item.classList.remove("selected");
        });

        // 清空日期选择
        startDate.value = "";
        endDate.value = "";

        // 恢复排序按钮状态
        ascendingOrderButton.classList.remove("selected");
        descendingOrderButton.classList.remove("selected");

        // 清空搜索输入框
        searchInput.value = searchKeyword;

        // 更新显示收藏按钮状态
        showFavoritesButton.value = "0";
    });
    // 获取分页栏元素
    const pagination = document.getElementById("pagination");

    // 假设这里有一个变量 totalPages 包含了后端返回的总页数
    const totalPages = Math.ceil(totalDataCount / itemsPerPage);


    // 清空分页栏
    pagination.innerHTML = '';

    // 动态生成分页按钮
    for (let page = 1; page <= totalPages; page++) {
        const pageButton = document.createElement("li");
        pageButton.innerHTML = `<a href="#">${page}</a>`;
        pagination.appendChild(pageButton);
    }


    // 获取提交按钮元素
    const submitButton = document.getElementById("submitButton");


    // 首先确保文档已加载完毕
    document.addEventListener('DOMContentLoaded', function () {

        // 当用户选择输入语言后触发的事件处理程序
        document.getElementById('inputLanguageSelect').addEventListener('change', function () {
            const selectedInputLanguage = this.value; // 获取用户选择的输入语言
            const inputLanguageId = languageMapping[selectedInputLanguage]; // 映射为数字值
            // 将 inputLanguageId 发送到后端，可以使用 AJAX 或 Fetch API
        });

        // 当用户选择输出语言后触发的事件处理程序
        document.getElementById('outputLanguageSelect').addEventListener('change', function () {
            const selectedOutputLanguage = this.value; // 获取用户选择的输出语言
            const outputLanguageId = languageMapping[selectedOutputLanguage]; // 映射为数字值
            // 将 outputLanguageId 发送到后端，可以使用 AJAX 或 Fetch API
        });
    });

    // 在提交按钮点击事件处理程序中添加获取数据的逻辑
    submitButton.addEventListener("click", function () {
        // 构建数据对象
        const requestData = {
            input_language: languageMapping[selectedInputLanguage],
            output_language: languageMapping[selectedOutputLanguage],
            start_date: selectedStartDate,
            end_date: selectedEndDate,
            sort_order: sortOrder,
            favoritesValue: showFavoritesValue,
            search_keyword: searchKeyword,
        };
        // 使用fetch将数据对象发送到后端
        fetch("/user_translate_history", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
        })
            .then((response) => {
                // 在这里处理后端的响应
                if (response.status === 200) {
                    return response.json();
                }
            })
            // 在提交按钮点击事件处理程序中的fetch成功后的处理中
            .then((data) => {
                // 在这里处理从后端获取的数据
                if (data.data_list !== null) {
                    // 处理数据列表
                    console.log("数据列表:", data.data_list);
                    // 这里可以将数据显示在页面上，例如更新表格内容
                    updateTableWithData(data.data_list, data.total_pages, data.current_page);
                    // 更新分页信息
                    updatePagination(data.total_pages, data.current_page);
                } else {
                    console.log("未找到有效的数据列表。");
                }
            })
    });


    // 新增一个函数用于更新分页信息
    function updatePagination(totalPages, currentPage) {
        const pagination = document.getElementById("pagination");
        pagination.innerHTML = "";
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = i === currentPage ? "active" : "";
            const link = document.createElement("a");
            link.href = "#"; // 可以添加你的分页处理逻辑
            link.textContent = i;
            link.addEventListener("click", () => handlePageClick(i)); // 添加点击事件处理逻辑
            li.appendChild(link);
            pagination.appendChild(li);
        }
    }

    // 新增一个函数用于更新表格内容
    function updateTableWithData(dataList, totalPages, currentPage) {
        // 在这里根据后端返回的数据列表更新表格内容
        const tableBody = document.querySelector("table tbody");
        tableBody.innerHTML = "";  // 清空表格内容
        dataList.forEach((item, index) => {
            const tableRow = document.createElement("tr");
            tableRow.className = index % 2 === 0 ? "success" : "active";
            // 根据需要显示的列创建对应的 <td> 元素
            const columnsToShow = [0, 1, 2, 3]; // 选择要显示的列的索引
            columnsToShow.forEach(colIndex => {
                const tableData = document.createElement("td");
                tableData.textContent = item[colIndex];
                tableRow.appendChild(tableData);
            });
            // 添加操作列
            const operationCell = document.createElement("td");
            const btnContainer = document.createElement("div");
            btnContainer.className = "btn-container";

            const updateForm = document.createElement("form");
            updateForm.method = "POST";
            updateForm.action = "/update_translation_item";
            const updateButton = createButton("更新", "btn btn-primary btn-xs");

            const deleteForm = document.createElement("form");
            deleteForm.method = "POST";
            deleteForm.action = "/delete_translation_list";
            const deleteButton = createButton("删除", "btn btn-danger btn-xs");

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

        // 更新分页信息
        updatePagination(totalPages, currentPage);
    }

// 新增一个函数用于创建按钮元素
    function createButton(text, className) {
        const button = document.createElement("button");
        button.type = "submit";
        button.className = className;
        button.textContent = text;
        return button;
    }
// 新增一个函数用于更新分页信息
    function updatePagination(totalPages, currentPage) {
        const pagination = document.getElementById("pagination");
        pagination.innerHTML = "";

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = i === currentPage ? "active" : "";

            const link = document.createElement("a");
            link.href = "#"; // 添加你的分页处理逻辑
            link.textContent = i;

            li.appendChild(link);
            pagination.appendChild(li);
        }
    }
// 新增一个函数用于更新分页信息
    function updatePagination(totalPages, currentPage) {
        const pagination = document.getElementById("pagination");
        pagination.innerHTML = "";
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = i === currentPage ? "active" : "";
            const link = document.createElement("a");
            link.href = "#"; // 可以添加你的分页处理逻辑
            link.textContent = i;
            link.addEventListener("click", () => handlePageClick(i)); // 添加点击事件处理逻辑
            li.appendChild(link);
            pagination.appendChild(li);
        }
    }

// 新增一个函数用于处理分页按钮点击事件
    function handlePageClick(pageNumber) {
        // 在这里可以处理点击分页按钮的逻辑
        // 例如，可以发起后端请求获取对应页的数据，然后调用 updateTableWithData 更新表格内容
        console.log("Clicked on page", pageNumber);

        // 构建数据对象
        const requestData = {
            input_language: selectedInputLanguage,
            output_language: selectedOutputLanguage,
            start_date: selectedStartDate,
            end_date: selectedEndDate,
            sort_order: sortOrder,
            favoritesValue: showFavoritesValue,
            search_keyword: searchKeyword,
            page: pageNumber, // 将点击的页码传递到后端
        };

        // 使用 fetch 将数据对象发送到后端
        fetch("/user_translate_history", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
        })
            .then((response) => {
                // 在这里处理后端的响应
                if (response.status === 200) {
                    return response.json();
                }
            })
            // 在 fetch 成功后的处理中
            .then((data) => {
                // 在这里处理从后端获取的数据
                if (data.data_list !== null) {
                    // 处理数据列表
                    console.log("数据列表:", data.data_list);

                    // 这里可以将数据显示在页面上，例如更新表格内容
                    updateTableWithData(data.data_list, data.total_pages, data.current_page);
                } else {
                    console.log("未找到有效的数据列表。");
                }
            })
    }

    // 更新按钮点击事件
    updateButton.addEventListener("click", function () {
        const updateForm = event.target.closest("form");
        const itemId = updateForm.querySelector('input[name="nid"]').value;

        // 发送请求到后端
        fetch("/update_translation_item", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({id: itemId, status: 1}), // 假设这里传递状态值 1
        })
            .then((response) => {
                if (response.status === 200) {
                    return response.json();
                }
            })
            .then((data) => {
                // 根据后端返回的状态值更新按钮状态
                if (data.status === 1) {
                    // 状态值为 1，显示红心
                    updateButton.textContent = '❤️';
                } else {
                    // 状态值为 0，显示更新
                    updateButton.textContent = '更新';
                }
            })
            .catch((error) => {
                console.error("Error updating status:", error);
            });
    });

});

