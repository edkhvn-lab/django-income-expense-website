const searchField = document.querySelector("#searchField");

const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const noResults = document.querySelector(".no-results");
const tbody = document.querySelector(".table-body");

// стартовое состояние
tableOutput.style.display = "none";
noResults.style.display = "none";

function showDefaultTable() {
  appTable.style.display = "block";
  tableOutput.style.display = "none";
  noResults.style.display = "none";
  paginationContainer.style.display = "block";
  tbody.innerHTML = "";
}

searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value.trim();

  // 🟢 пустой input → обычная таблица
  if (searchValue.length === 0) {
    showDefaultTable();
    return;
  }

  // 🔵 режим поиска
  appTable.style.display = "none";
  paginationContainer.style.display = "none";
  tableOutput.style.display = "block";
  noResults.style.display = "none";

  fetch("/search-expenses/", {
    method: "POST",
    body: JSON.stringify({ searchText: searchValue }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      // 🔴 нет результатов
      if (data.length === 0) {
        tableOutput.style.display = "none";
        noResults.style.display = "block";
        tbody.innerHTML = "";
        return;
      }

      // 🟢 есть результаты
      noResults.style.display = "none";
      tableOutput.style.display = "block";

      tbody.innerHTML = data
        .map(
          (item) => `
            <tr>
              <td>${item.amount}</td>
              <td>${item.category}</td>
              <td>${item.description}</td>
              <td>${item.date}</td>
              <td>
                <a href="/edit-expense/${item.id}/" class="btn btn-secondary btn-sm">
                  Edit
                </a>
              </td>
            </tr>
          `
        )
        .join("");
    })
    .catch((err) => {
      console.error("Search error:", err);
    });
});

