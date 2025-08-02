document.addEventListener('DOMContentLoaded', () => {
    class App {
        constructor() {
            this.init();
        }

        init() {
            if (document.querySelector('.custom-dropdown')) {
                new CustomDropdownHandler();
            }

            const weatherForm = document.getElementById('weatherForm');
            if (weatherForm) {
                new WeatherFormHandler(weatherForm);
            }

            const forecastForm = document.getElementById('forecastForm');
            if (forecastForm) {
                new ForecastPageHandler(forecastForm);
            }
        }
    }

    class CustomDropdownHandler {
        constructor() {
            this.dropdowns = document.querySelectorAll('.custom-dropdown');
            this.init();
        }

        init() {
            this.dropdowns.forEach(dropdown => this.setupDropdown(dropdown));

            document.addEventListener('click', (e) => {
                this.dropdowns.forEach(dropdown => {
                    if (dropdown.classList.contains('open') && !dropdown.contains(e.target)) {
                        this.closeDropdown(dropdown);
                    }
                });
            });
        }

        setupDropdown(dropdown) {
            const trigger = dropdown.querySelector('.dropdown-trigger');
            const menu = dropdown.querySelector('.dropdown-menu');
            const options = menu.querySelectorAll('li');
            const hiddenInput = document.getElementById(dropdown.dataset.targetInput);
            const selectedDisplay = trigger.querySelector('span');

            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = dropdown.classList.contains('open');
                this.dropdowns.forEach(d => this.closeDropdown(d));
                if (!isOpen) {
                    this.openDropdown(dropdown);
                }
            });

            options.forEach(option => {
                option.addEventListener('click', () => {
                    hiddenInput.value = option.dataset.value;
                    selectedDisplay.textContent = option.textContent.trim();

                    menu.querySelector('.selected')?.classList.remove('selected');
                    option.classList.add('selected');

                    this.closeDropdown(dropdown);

                    hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
                });
            });
        }

        openDropdown(dropdown) {
            dropdown.classList.add('open');
        }

        closeDropdown(dropdown) {
            dropdown.classList.remove('open');
        }
    }

    class WeatherFormHandler {
        constructor(formElement) {
            this.form = formElement;
            this.errorMessage = document.getElementById('error-message');
            this.submitBtn = this.form.querySelector('.submit-btn');
            this.inputSections = this.form.querySelectorAll('.input-section');
            this.init();
        }

        init() {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
            document.getElementById('choice').addEventListener('change', this.handleChoiceChange.bind(this));
            document.getElementById('coord_type').addEventListener('change', this.handleCoordTypeChange.bind(this));
        }

        handleChoiceChange(e) {
            this.hideAllSections();
            this.hideError();

            const choice = e.target.value;
            const sections = {
                '1': 'city_input',
                '2': 'coords_input',
                '3': 'zip_input',
            };

            if (sections[choice]) {
                setTimeout(() => this.showSection(sections[choice]), 100);
            }
        }

        handleCoordTypeChange(e) {
            const coordType = e.target.value;
            const decimalSection = document.getElementById('decimal_coords');
            const dmsSection = document.getElementById('dms_coords');

            decimalSection.classList.remove('active');
            dmsSection.classList.remove('active');

            const sections = {
                '1': decimalSection,
                '2': dmsSection,
            };

            if (sections[coordType]) {
                setTimeout(() => sections[coordType].classList.add('active'), 150);
            }
        }

        handleSubmit(event) {
            const { valid, missingFields } = this.validateForm();

            if (!valid) {
                event.preventDefault();
                this.showError(`Missing: ${missingFields.join(', ')}`);
            } else {
                this.setLoadingState(true);
            }
        }

        validateForm() {
            const choice = document.getElementById('choice').value;
            let valid = true;
            let missingFields = [];

            this.clearErrorStates();

            if (choice === '1') {
                missingFields = this.validateFields([{ id: 'city', name: 'City name' }]);
            } else if (choice === '2') {
                const coordType = document.getElementById('coord_type').value;
                if (coordType === '1') {
                    missingFields = this.validateFields([
                        { id: 'lat', name: 'Latitude' },
                        { id: 'lon', name: 'Longitude' }
                    ]);
                } else if (coordType === '2') {
                    missingFields = this.validateFields([
                        { id: 'lat_deg', name: 'Latitude degrees' }, { id: 'lat_min', name: 'Latitude minutes' },
                        { id: 'lat_sec', name: 'Latitude seconds' }, { id: 'lat_dir', name: 'Latitude direction' },
                        { id: 'lon_deg', name: 'Longitude degrees' }, { id: 'lon_min', name: 'Longitude minutes' },
                        { id: 'lon_sec', name: 'Longitude seconds' }, { id: 'lon_dir', name: 'Longitude direction' }
                    ]);
                } else {
                    missingFields.push('Coordinate type');
                }
            } else if (choice === '3') {
                missingFields = this.validateFields([
                    { id: 'zip_code', name: 'Zip/Postal code' },
                    { id: 'country_code', name: 'Country code' }
                ]);
            } else {
                missingFields.push('Input method');
            }

            valid = missingFields.length === 0;
            return { valid, missingFields };
        }

        validateFields(fieldsToValidate) {
            const missing = [];
            fieldsToValidate.forEach(field => {
                const element = document.getElementById(field.id);
                if (!element.value.trim()) {
                    missing.push(field.name);
                    this.addErrorState(element);
                }
            });
            return missing;
        }

        hideAllSections() {
            this.inputSections.forEach(section => section.classList.remove('active'));
        }

        showSection(sectionId) {
            document.getElementById(sectionId)?.classList.add('active');
        }

        addErrorState(element) {
            element.style.borderColor = 'rgba(244, 67, 54, 0.8)';
            element.style.backgroundColor = 'rgba(244, 67, 54, 0.1)';
        }

        clearErrorStates() {
            this.form.querySelectorAll('input, select').forEach(elem => {
                elem.style.borderColor = '';
                elem.style.backgroundColor = '';
            });
        }

        showError(message) {
            this.errorMessage.textContent = message;
            this.errorMessage.style.display = 'block';
            setTimeout(() => this.hideError(), 5000);
        }

        hideError() {
            this.errorMessage.style.display = 'none';
        }

        setLoadingState(isLoading) {
            if (isLoading) {
                this.form.classList.add('loading');
                this.submitBtn.textContent = 'Loading Weather Data...';
            } else {
                this.form.classList.remove('loading');
            }
        }
    }


    class ForecastPageHandler {
        constructor(formElement) {
            this.form = formElement;
            this.submitBtn = this.form.querySelector('.btn-primary');
            this.radioGroups = document.querySelectorAll('.radio-group');
            this.originalButtonText = this.submitBtn.innerHTML;
            this.init();
        }

        init() {
            this.form.addEventListener('submit', () => {
                this.setLoadingState(true);

                setTimeout(() => {
                    this.setLoadingState(false);
                }, 1500);
            });

            this.setupRadioGroups();
        }

        setLoadingState(isLoading) {
            if (isLoading) {
                this.form.classList.add('loading');
                this.submitBtn.innerHTML = '📊 Loading Forecast Data...';
                this.submitBtn.disabled = true;
                this.radioGroups.forEach(group => {
                    group.style.pointerEvents = 'none';
                    group.style.opacity = '0.6';
                });
            } else {
                this.form.classList.remove('loading');
                this.submitBtn.innerHTML = this.originalButtonText;
                this.submitBtn.disabled = false;
                this.radioGroups.forEach(group => {
                    group.style.pointerEvents = '';
                    group.style.opacity = '';
                });
            }
        }

        setupRadioGroups() {
            const initiallyChecked = document.querySelector('.radio-group input:checked');
            if (initiallyChecked) {
                initiallyChecked.closest('.radio-group').classList.add('active');
            }

            this.radioGroups.forEach(group => {
                group.addEventListener('click', () => {
                    this.radioGroups.forEach(g => g.classList.remove('active'));
                    group.classList.add('active');
                    group.querySelector('input[type="radio"]').checked = true;
                });
            });
        }
    }

    new App();
});