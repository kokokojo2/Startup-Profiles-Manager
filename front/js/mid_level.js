async function load_profile_list(mode) {
    let profiles_obj = await eel.get_profile_list()();
    profiles_obj = JSON.parse(profiles_obj);

    let help_text = document.createElement('p');

    if (profiles_obj.status === "OK"){
        if (mode === "main_menu") {
            help_text.innerHTML = "Please, choose a profile to launch.";

        }

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
    let settings = await  eel.get_settings()();
    settings = JSON.parse(settings);
    profile_info = JSON.parse(profile_info);
    choose_profile(profile_info);

    if (settings.close_after_launch) {
        let action = document.createElement("div");
        action.className = "action";
        action.id = `close`

        action.innerHTML = `<p>Close application</p>`;
        document.getElementsByClassName("actions")[0].appendChild(action);
    }

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

    let help_text = document.getElementById('close');
    if (help_text) {
        setTimeout(function(){
            help_text.innerHTML = "Closing application in 3..";
            setTimeout(function() {
                help_text.innerHTML = "Closing application in 2..";
                setTimeout(function(){
                    help_text.innerHTML = "Closing application in 1..";
                    setTimeout(function(){
                        window.close();
                            }, 1000);
                    }, 1000);
                }, 1000);
        }, 1000);
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

function parse_profile(mode) {
    let profile_obj = {
            name: document.getElementsByClassName("profile-name-detail")[0].value,
            timeout_mode: document.getElementById("timeout_mode").checked,
            entries: []
        }
    let entries = document.getElementsByClassName("profile-entry");
        let disabled_parse = document.getElementsByClassName("option");
        let i = 0;
    for (let entry of entries) {
        let entry_obj = {
            name: entry.children[0].children[0].value,
            priority: entry.children[1].children[0].value,
            executable_path: entry.children[2].children[0].value,
            launch_time: profile_obj.timeout_mode ? entry.children[3].children[0].value : 0,
            id: mode === "create" ? null : entry.dataset.id,
            disabled: false,
        }
        if (entry_obj.id === undefined) {
            entry_obj.id = null;
        }

        if (mode !== "create") {
            entry_obj.disabled = !disabled_parse[i].children[0].children[0].children[0].checked;
            i++;
        }
        profile_obj.entries.push(entry_obj);
    }

    profile_obj.id = mode === "create" ? null : document.getElementById("profile-id").dataset.id;
    console.log(profile_obj);
    return profile_obj;
}

async function save_profile(mode) {
    let right_info_bar = document.getElementsByClassName("right-popup")[0];
    while (right_info_bar.firstChild) {
        right_info_bar.removeChild(right_info_bar.firstChild);
        }

    let saving_spinner = document.createElement("div");
    saving_spinner.className = "message";
    saving_spinner.innerHTML = "<div>Saving</div><div class=\"spinner\"></div>";
    right_info_bar.appendChild(saving_spinner);

    let parsed_profile = parse_profile(mode);
    let response = await eel.save_profile(JSON.stringify(parsed_profile))();

    response = JSON.parse(response);
    if(response.status === "saved") {
        saving_spinner.innerHTML = "<div>Saved</div><div class=\"tick\" style='width: 10px; margin-top: -5px;'></div>";

        if (mode === "create") {
            clear_page();
            let info_text = document.createElement('div');
            info_text.className = "main-slogan";
            info_text.innerHTML = "<p class=\"big\" style='font-size: 26px; padding-top: 150px;'>Profile successfully saved. Visit Profiles page to view it.</p>";
            document.getElementById("contents").appendChild(info_text);
        }
        let entries = document.getElementsByClassName('profile-entry');
        let i = 0;
        for (let entry of entries) {
            if (!entry.hasAttribute("data-id")) {
                entry.setAttribute("data-id", response.new_entries_ids[i]);
                i++;
            }
        }
    }

    else {
        right_info_bar.removeChild(saving_spinner);
        for (let message of response.messages) {
            let message_div = document.createElement('div');
            message_div.className = "message";
            message_div.innerHTML = `<p>${message}</p>`;
            right_info_bar.appendChild(message_div);
        }
    }
    console.log(response);
}

async function delete_profile(event) {
    await eel.delete_profile(event.target.parentElement.dataset.id)();
    event.target.parentElement.remove();
}
function add_remove_button() {
    let profile_containers = document.getElementsByClassName("profile-container");
    for (let container of profile_containers) {
        let trash_button = document.createElement("img");
        trash_button.setAttribute("src", "../resources/trash.png");
        trash_button.setAttribute("alt", "delete");

        trash_button.addEventListener("click", delete_profile);
        container.appendChild(trash_button);
    }
}

async function delete_entry(event) {
    let options_container = event.target.parentElement.parentElement.parentElement;
    let container = document.getElementById(`${options_container.id.split("-")[0]}-info`);
    await eel.delete_entry(container.dataset.id)();

    container.remove();
    options_container.remove();
}

function add_row() {
        let new_entry = document.createElement('tr');
        new_entry.className = "profile-entry"
        new_entry.id = `${get_next_rowid() + 1}-info`;

        let checkbox = document.querySelector("input[type=checkbox]");
        new_entry.innerHTML = "<td><input type=\"text\" class=\"table-cell\"></td>\n".repeat(2);
        new_entry.innerHTML += "<td><input type=\"text\" class=\"table-cell\" ondrop=\"dropHandler(event)\" placeholder=\"Drop .exe file or shortcut here.\"></td>";

        new_entry.innerHTML += checkbox.checked ? "<td><input type=\"text\" class=\"table-cell\"></td>" : "<td style='display: none;'><input type=\"text\" class=\"table-cell\"></td>"

        let tables = document.getElementsByTagName('table');
        tables[0].appendChild(new_entry);
        let options_row = document.createElement('tr');
        options_row.id = `${get_next_rowid()}-option`;
        options_row.className = 'option';
        options_row.innerHTML =  `<td style="padding-top: 3px"><div class="disable-checkbox"><input type="checkbox" checked></div></td>` +
                                 "<td><div style='height: 20px;'><img style='top: 0; padding-top: 4px; position: relative;' src=\"../resources/trash.png\" alt=\"delete\" onclick=\"delete_entry(event);\"></div></td>";
        tables[1].appendChild(options_row);
}

async function choose_profile_detail(event) {
    let profile_info = await eel.get_profile_info(event.target.dataset.id)();
    profile_info = JSON.parse(profile_info);
    clear_page();

    document.getElementById("contents").innerHTML = "" +
        "<div class=\"right-popup\"></div>" +
        `<div id='profile-id' style='display:none;' data-id='${profile_info.meta.id}'></div>` +
        "<div class=\"center-container\">" +
        `<input type=\"text\" class=\"profile-name-detail\" value=\"${profile_info.meta.name}\">` +
        "<div class=\"checkbox-wrapper\">" +
        "<p>Launch each entry with a delay</p>" +
        `<input type=\"checkbox\" id='timeout_mode' ${profile_info.meta.timeout_mode ? "checked" : ""}>` +
        "</div>" +
        "<div class=\"table-wrapper\">" +
        "<table style=\"width: 750px;\">" +
        "<tr id=\"head\">" +
        "<th style=\"width: 20%\">Name</th>" +
        "<th style=\"width: 10%\">Priority</th>" +
        "<th style=\"width: 60%\">Path to executable</th>" +
        `${profile_info.meta.timeout_mode ? "<th style=\"width: 15%\">Timeout</th>" : "<th style=\"display: none;\">Timeout</th>"}` +
        "</tr>" +
        "<tr class=\"space1\"></tr>" +
        "</table>" +
        "<table class=\"options\">" +
        "<tr>" +
        "<th></th>" +
        "<th></th>" +
        "</tr>" +
        "<tr class=\"space1\"></tr>" +
        "</table>" +
        "</div>" +
        "<button id=\"add-entry\" style=\"width: 40%;\" onclick=\"add_row();\">+</button>" +
        "<button id=\"save\" onclick=\"save_profile('update');\">Save</button>" +
        "</div>"

        document.querySelector("input[type=checkbox]").addEventListener("change", function () {
            if (this.checked) {
                document.getElementById("head").lastElementChild.setAttribute("style", "width: 15%");
                let table_rows = document.getElementsByClassName("profile-entry");
                for (let row of table_rows) {
                    if (row.id !== "head" && row.className !== "space1") {
                        row.lastElementChild.removeAttribute("style");
                    }
                }
            } else {
                let head_row = document.getElementById("head");
                head_row.lastElementChild.setAttribute("style", "display: none;");

                let table_rows = document.getElementsByClassName("profile-entry");
                for (let row of table_rows) {
                    if (row.id !== "head" && row.className !== "space1") {
                        row.lastElementChild.setAttribute("style", "display: none;");
                    }
                }
            }
        });


        let table = document.getElementsByTagName("table")[0];
        let options_table = document.getElementsByTagName("table")[1];
        if (profile_info.meta.timeout_mode) {
                let head_row = document.getElementById("head");
                head_row.setAttribute("style", "width: 15%;");
            }

        for (let entry of profile_info.entries) {
            let table_row = document.createElement("tr");
            table_row.className = "profile-entry";
            table_row.setAttribute("data-id", entry.id);
            table_row.id = `${get_next_rowid() + 1}-info`;

            table_row.innerHTML = `<td><input type=\"text\" class=\"table-cell\" value="${entry.name}"></td>` +
                `<td><input type=\"text\" class=\"table-cell\" value="${entry.priority}"></td>` +
                `<td><input type=\"text\" class=\"table-cell\" ondrop=\"dropHandler(event)\" value = "${entry.executable_path}" placeholder=\"Drop .exe file or shortcut here.\"></td>`;

            if (profile_info.meta.timeout_mode) {
                table_row.innerHTML += `<td><input type=\"text\" class=\"table-cell\" value="${entry.launch_time}"></td>`
            }
            else {
                table_row.innerHTML += "<td style='display: none;'><input type=\"text\" class=\"table-cell\"></td>"
            }
            table.appendChild(table_row);
            let options = document.createElement("tr");
            options.id = `${get_next_rowid()}-option`;
            options.className = "option";
            options.innerHTML = `<td style="padding-top: 3px"><div class="disable-checkbox"><input type="checkbox" ${entry.disabled ? "" : "checked"}></div></td>` +
                                 "<td><div style='height: 20px;'><img style='top: 0; padding-top: 4px; position: relative;' src=\"../resources/trash.png\" alt=\"delete\" onclick=\"delete_entry(event);\"></div></td>";

            options_table.appendChild(options);
        }
}

function get_next_rowid() {
    return document.getElementsByClassName("profile-entry").length;
}


async function load_settings() {
    let settings = JSON.parse(await eel.get_settings()());
    if (settings.close_after_launch) {
        document.getElementById("close-after-launch").setAttribute("checked", "");
    }
    if (settings.start_with_windows) {
        document.getElementById("start-with-windows").setAttribute("checked", "");
    }

}