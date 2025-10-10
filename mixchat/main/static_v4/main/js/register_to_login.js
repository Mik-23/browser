//let currentCode = ''
//const country_code = { "Afghanistan": "+93", "Albania": "+355", "Algeria": "+21",
//                           "American Samoa": "+684", "Andorra": "+376", "Angola": "+244", "Anguilla": "+1-264",
//                           "Antigua and Barbuda": "+1-268", "Armenia": "+374", "Argentina": "+54", "Australia": "+61",
//                           "Austria": "+43", "Azerbaijan": "+994", "Bahamas": "+1-242", "Bahrain": "+973",
//                           "Bangladesh": "+880", "Barbados": "+1-246", "Belarus": "+375", "Belgium": "+32", "Belize": "+501",
//                           "Benin": "+229", "Bermuda": "+1-441", "Bolivia": "+591", "Bosnia and Herzegovina": "+387",
//                           "Botswana": "+267", "Brazil": "+55", "British Virgin Islands": "+1-284", "Brunei Darusalaam": "+673",
//                           "Bulgaria": "+359", "Burkina Faso": "+226", "Burundi": "+257", "Byelorussian": "+7",
//                           "Cambodia": "+855", "Cameroon": "+237", "Canada": "+1", "Cape Verde": "+238", "Cayman Islands": "+1-345",
//                           "Central African Republic": "+236", "Chad": "+235", "Chile": "+56", "China": "+86",
//                           "Christmas Island": "+672", "Cocos Islands": "+672", "Colombia": "+57",
//                           "Commonwealth of the Northern Mariana Islands": "+1-670", "Comoros and Mayotte Island": "+269",
//                           "Congo": "+242", "Cook Islands": "+682", "Costa Rica": "+506", "Croatia": "+385", "Cuba": "+53",
//                           "Cyprus": "+357", "Czech Republic": "+420", "Denmark": "+45", "Diego Garcia": "+246", "Djibouti": "+253",
//                           "Dominica": "+1-767", "Dominican Republic": "+1-809", "East Timor": "+62", "Ecuador": "+593",
//                           "Egypt": "+20", "El Salvador": "+503", "Equatorial Guinea": "+240", "Estonia": "+372",
//                           "Ethiopia": "+251", "Faeroe Islands": "+298", "Falkland Islands": "+500", "Fiji": "+679",
//                           "Finland": "+358", "France": "+33", "French Antilles": "+590", "French Guiana": "+594",
//                           "French Polynesia": "+689", "Gabon": "+241", "Gambia": "+220", "Georgia": "+995", "Germany": "+49",
//                           "Ghana": "+233", "Gibraltar": "+350", "Greece": "+30", "Greenland": "+299", "Grenada": "+1-473",
//                           "Guam": "+1-671, +671", "Guatemala": "+502", "Guinea": "+224", "Guinea-Bissau": "+245", "Guyana": "+592",
//                           "Haiti": "+509", "Honduras": "+504", "Hong Kong": "+852", "Hungary": "+36", "Iceland": "+354",
//                           "India": "+91", "Indonesia": "+62", "Iran": "+98", "Iraq": "+964", "Irish Republic": "+353",
//                           "Israel": "+972", "Italy": "+39", "Ivory Coast": "+225", "Jamaica": "+1-876", "Japan": "+81",
//                           "Jordan": "+962", "Kazakhstan": "+7", "Kenya": "+254", "Kiribati Republic": "+686",
//                           "Kirg(h)izia": "+996", "Kuwait": "+965", "Laos": "+856", "Latvia": "+371", "Lebanon": "+961",
//                           "Lesotho": "+266", "Liberia": "+231", "Libya": "+21", "Liechtenstein": "+41", "Lithuania": "+370",
//                           "Luxembourg": "+352", "Macao": "+853", "Macedonia": "+389", "Madagascar": "+261", "Malawi": "+265",
//                           "Malaysia": "+60", "Maldives": "+960", "Mali": "+223", "Malta": "+356", "Marshall Islands": "+692",
//                           "Martinique": "+596", "Mauritania": "+222", "Mauritius": "+230", "Mexico": "+1-706, +1-905, +52",
//                           "Micronesia": "+691", "Monaco": "+377", "Mongolia": "+976", "Montserrat": "+1-664", "Morocco": "+212",
//                           "Mozambique": "+258", "Myanmar": "+95", "Namibia": "+264", "Nauru": "+674", "Nepal": "+977",
//                           "Netherlands": "+31", "Netherlands Antilles": "+599", "New Caledonia": "+687", "New Zealand": "+64",
//                           "Nicaragua": "+505", "Niger": "+227", "Nigeria": "+234", "Niue": "+683", "Norfolk Island": "+672",
//                           "North Korea": "+850", "North Yemen": "+967", "Northern Mariana Islands": "+670", "Norway": "+47",
//                           "Oman": "+968", "Pakistan": "+92", "Panama": "+507", "Papua New Guinea": "+675", "Paraguay": "+595",
//                           "Peru": "+51", "Philippines": "+63", "Poland": "+48", "Portugal": "+351", "Puerto Rico": "+1-787",
//                           "Qatar": "+974", "Republic of San Marino": "+378", "Reunion": "+262", "Romania": "+40",
//                           "Russia": "+7", "Rwandese Republic": "+250", "Saint Helena and Ascension Island": "+247",
//                           "Saint Pierre et Miquelon": "+508", "San Marino": "+39", "Sao Tome e Principe": "+239",
//                           "Saudi Arabia": "+966", "Senegal": "+221", "Seychelles": "+248", "Sierra Leone": "+232",
//                           "Singapore": "+65", "Slovakia": "+421", "Slovenia": "+386", "Solomon Islands": "+677",
//                           "Somalia": "+252", "South Africa": "+27", "South Korea": "+82", "South Yemen": "+969",
//                           "Spain": "+34", "Sri Lanka": "+94", "St.Kitts and Nevis": "+1-869", "St.Lucia": "+1-758",
//                           "St.Vincent and the Grenadines": "+1-784", "Sudan": "+249", "Suriname": "+597",
//                           "Svalbard and Jan Mayen Islands": "+47", "Swaziland": "+268", "Sweden": "+46", "Switzerland": "+41",
//                           "Syria": "+963", "Ta(d)jikistan": "+992", "Taiwan": "+886", "Tanzania": "+255", "Thailand": "+66",
//                           "Togolese Republic": "+228", "Tokelau": "+690", "Tonga": "+676", "Trinidad and Tobago": "+1-868",
//                           "Tunisia": "+21", "Turkey": "+90", "Turkmenistan": "+993", "Turks & Caicos Islands": "+1-649",
//                           "Tuvalu": "+688", "US Virgin Islands": "+1-340", "Uganda": "+256", "Ukraine": "+380",
//                           "United Arab Emirates": "+971", "United Kingdom": "+44", "Uruguay": "+598", "USA": "+1",
//                           "Uzbekistan": "+998", "Vanuatu": "+678", "Vatican City": "+39", "Venezuela": "+58", "Vietnam": "+84",
//                           "Wallis and Futuna Islands": "+681", "Western Sahara": "+21", "Western Samoa": "+685",
//                           "Yugoslavia": "+381", "Zaire": "+243", "Zambia": "+260", "Zimbabwe": "+263" }
//
//function displayCountry () {
//    countryList = document.getElementById("selectCountry")
//    countryList.innerHTML = ''
//    for (country in country_code) {
//        elem = document.createElement("option")
//        elem.textContent = country
//        elem.value = country
//        countryList.appendChild(elem)
//    }
//}
//
//function countryToCode() {
//    const select = document.getElementById('selectCountry')
//    const selectedCountry = select.value
//    const code = country_code[selectedCountry]
//    return code
//}
//
//var element = document.getElementById('reg_phone');
//const mask = IMask(element, {
//    mask: '', // начальный шаблон пустой
//    lazy: false
//});
//
//// Обработчик изменения страны
//document.getElementById('selectCountry').addEventListener('change', () => {
//    currentCode = countryToCode(); // получаете актуальный код
//    if (currentCode) {
//        mask.updateOptions({ mask: `${currentCode}(000)000-00-00` });
//    }
//});

document.getElementById('registerForm').addEventListener('submit', (event) => {
    event.preventDefault(); // Предотвращаем стандартное поведение формы
    const email = document.getElementById('reg_email').value; // Получаем значение email
    const username = document.getElementById('reg_login').value; // Получаем значение логина
    const password = document.getElementById('reg_password').value; // Получаем значение пароля
    //const country_code = currentCode;

    fetch('/api/reg/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({email, username, password }),
    })
    .then(response => {
        return response.json().then(data => ({ data, status: response.status })); // Возвращаем объект с данными и статусом
    })
    .then(({ data, status }) => {
        console.log(data);
        if (status === 200) { // Проверяем статус ответа
            window.location.href = data.login_url; // Перенаправляем пользователя на страницу авторизации
        } else {
            console.error(data); // Обработка ошибок
        }
    })
    .catch(error => console.error('Ошибка:', error)); // Обработка сетевых ошибок
});

//window.onload = () => {
//    displayCountry();
//};
