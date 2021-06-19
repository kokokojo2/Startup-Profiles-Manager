async function load_profile_list() {
    let profiles_obj = await eel.get_profile_list()();
    profiles_obj = JSON.parse(profiles_obj);
    console.log(profiles_obj);

    let profiles_array = [];
    for(let i = 0; i < profiles_obj.length; i++) {
        console.log(i);

        let container = document.createElement("div");
        container.setAttribute("data-id", profiles_obj[i].id);
        container.className = "profile-container";
        container.innerHTML = `<a><p class=\"profile-name\">${profiles_obj[i]['name']}</p></a>\n` +
                              `<p class=\"apps-counter\">${profiles_obj[i].entries_count} apps</p>`;
        console.log(container);
        profiles_array.push(container);

        if (profiles_array.length === 4 || i === profiles_obj.length - 1) {
            let row = document.createElement("div");
            row.className = "row";
            for(let profile of profiles_array) {
                row.appendChild(profile);
            }
            document.getElementsByClassName("profile-tiles")[0].appendChild(row);
            profiles_array = [];
        }
    }


}

function choose_profile(profile) {

}