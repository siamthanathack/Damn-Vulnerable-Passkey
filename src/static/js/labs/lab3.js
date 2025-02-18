// This project was developed by Siam Thanat Hack Co., Ltd. (STH).
// Website: https://sth.sh  
// Contact: pentest@sth.sh
async function search_user() {
    const query = document.getElementById("query").value.trim();
    const apiSearchUserResp = await fetch("/lab3/api/search_user", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: query
        })
    });
    if (apiSearchUserResp.status != 200) {
        alert(await apiSearchUserResp.text());
        return;
    }
    const apiResult = await apiSearchUserResp.json();
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = ''; // Clear previous results

    // Check if the result is an array (list)
    if (apiResult.length === 0) {
        resultDiv.innerHTML = '<p>No results found.</p>';
    }
    else {
        apiResult.forEach(item => {
            // For each item in the list, create a div and add it to the result
            const itemDiv = document.createElement('div');
            itemDiv.classList.add('item');
            itemDiv.innerHTML = `
                <p>${item.username}</p>
            `;
            resultDiv.appendChild(itemDiv);
        });
    }
}

async function authenticate() {
    const username = document.getElementById("username").value.trim();
    if (username) {
        const apiAuthOptsResp = await fetch('/lab3/api/authentication_start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username
            })
        });
        if (apiAuthOptsResp.status != 200) {
            alert(await apiAuthOptsResp.text());
            return;
        }
        const authenticationOptionsJSON = await apiAuthOptsResp.json();
        const authResp = await startAuthentication(authenticationOptionsJSON);
        const apiAuthVerResp = await fetch('/lab3/api/authentication_verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: username,
              response: authResp,
            }),
        });
        alert(await apiAuthVerResp.text())
    } else {
        alert("Please enter a valid username.");
    }
}
