async function load_profile_list() {
    let profiles_obj = await eel.get_profile_list()();
    profiles_obj = JSON.parse(profiles_obj);

    let help_text = document.createElement('p');

    if (profiles_obj.status === "OK"){
        help_text.innerHTML = "Please, choose a profile to launch.";

        profiles_obj = profiles_obj.data;
        let profiles_array = [];
        for(let i = 0; i < profiles_obj.length; i++) {
            let container = document.createElement("div");
            container.setAttribute("data-id", profiles_obj[i].id);
            container.className = "profile-container";
            container.innerHTML = `<a><p class=\"profile-name\" data-id="${profiles_obj[i].id}">${profiles_obj[i]['name']}</p></a>\n` +
                                  `<p class=\"apps-counter\" data-id="${profiles_obj[i].id}">${profiles_obj[i].entries_count} apps</p>`;

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
    } else {
        help_text.innerHTML = "You do not have any profiles to launch. Please, create one first.";
    }
    document.getElementsByClassName("main-slogan")[0].appendChild(help_text);
}

async function choose_profile(profile_info) {
    clear_page();
    let center_wrap = document.createElement("div");
    center_wrap.className = "center-wrap";

    let main_slogan = document.createElement("div");
    main_slogan.className = "main-slogan";

    main_slogan.innerHTML = `<p class=\"big\" style=\"font-size: 30px; padding-bottom: 10px;\">Launching ${profile_info.meta.name}</p>` +
                            `<div class=\"gradient-line\"></div>`;

    let actions = document.createElement("div");
    actions.className = "actions";

    for (let [i, entry] of profile_info.entries.entries()) {
        if (! entry.disabled) {
            let action = document.createElement("div");
            action.className = "action";
            action.id = `entry-${entry.id}`

            action.innerHTML = `<p>${entry.name}</p>`;
            actions.appendChild(action);

            if(profile_info.meta.timeout_mode && i !== profile_info.entries.length - 1) {
                let timeout_action = document.createElement("div");
                timeout_action.className = "action";

                timeout_action.innerHTML += `<p>Timeout ${entry.launch_time} min</p>`;
                actions.appendChild(timeout_action);
            }
        }
    }

    let main_div = document.getElementById("contents");

    center_wrap.appendChild(main_slogan);
    center_wrap.appendChild(actions);
    main_div.appendChild(center_wrap);

    await eel.launch_profile(profile_info.meta.id)();
}

async function on_launch_profile(event) {
    let profile_info = await eel.get_profile_info(event.target.dataset.id)();
    profile_info = JSON.parse(profile_info);
    choose_profile(profile_info);

    for (let entry of profile_info.entries) {
        let spinner = document.createElement("div");
        spinner.className = "spinner";
        document.getElementById(`entry-${entry.id}`).appendChild(spinner);

        await new Promise(r => setTimeout(r, 500));
        spinner.className = "tick";
        if (profile_info.meta.timeout_mode) {
            let timeout_spinner = document.createElement("div");
            timeout_spinner.className = "spinner";
            document.getElementById(`entry-${entry.id}`).nextSibling.appendChild(timeout_spinner);
            await new Promise(r => setTimeout(r, entry.launch_time * 60 * 1000));
            timeout_spinner.className = "tick";
        }
    }
}

function clear_page() {
    let main_div = document.getElementById("contents");
    while (main_div.firstChild) {
        main_div.removeChild(main_div.firstChild);
    }
}

async function update_settings() {
    let setting1 = document.getElementById("start-with-windows");
    let setting2 = document.getElementById("close-after-launch");

    let settings_obj = {
        close_after_launch: setting2.checked,
        enable_startup: setting1.checked
    };

    console.log(JSON.stringify(settings_obj));
    await eel.update_settings(JSON.stringify(settings_obj))();

}
