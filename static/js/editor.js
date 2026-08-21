const raw = JSON.parse(document.getElementById('resumeData').textContent);

let state = {
    ...raw,
    github: raw.github || '',
    education: Array.isArray(raw.education) ? raw.education : [],
    experience: Array.isArray(raw.experience) ? raw.experience : [],
    skills: Array.isArray(raw.skills) ? raw.skills : [],
    projects: Array.isArray(raw.projects) ? raw.projects : [],
    certifications: Array.isArray(raw.certifications) ? raw.certifications : []
};

const form = document.getElementById('resumeForm');

const esc = s =>
    String(s ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');

const item = (title, html) => `
<div class="item-card">
    <button type="button" class="delete"
        onclick="this.closest('.item-card').remove(); sync()">♧</button>

    <h3 style="margin:0 0 10px;font-size:13px">${title}</h3>

    ${html}
</div>
`;

function renderCollections() {

    document.getElementById('educationItems').innerHTML =
        state.education.map((x, i) =>
            item('Education', `
                <div class="item-grid">

                    <label>
                        Institution
                        <input
                            data-c="education"
                            data-i="${i}"
                            data-k="institution"
                            value="${esc(x.institution)}">
                    </label>

                    <label>
                        Degree
                        <input
                            data-c="education"
                            data-i="${i}"
                            data-k="degree"
                            value="${esc(x.degree)}">
                    </label>

                    <label>
                        Field of study
                        <input
                            data-c="education"
                            data-i="${i}"
                            data-k="field_of_study"
                            value="${esc(x.field_of_study)}">
                    </label>

                    <label>
                        Level
                        <select
                            data-c="education"
                            data-i="${i}"
                            data-k="level">

                            <option ${x.level === "Bachelor's" ? 'selected' : ''}>
                                Bachelor's
                            </option>

                            <option ${x.level === 'Master' ? 'selected' : ''}>
                                Master
                            </option>

                            <option ${x.level === 'Diploma' ? 'selected' : ''}>
                                Diploma
                            </option>

                            <option ${x.level === 'School / None' ? 'selected' : ''}>
                                School / None
                            </option>

                        </select>
                    </label>

                    <label>
                        Start year
                        <input
                            data-c="education"
                            data-i="${i}"
                            data-k="start_year"
                            value="${esc(x.start_year)}">
                    </label>

                    <label>
                        End year
                        <input
                            data-c="education"
                            data-i="${i}"
                            data-k="end_year"
                            value="${esc(x.end_year)}">
                    </label>

                    <label>
                        Grade / CGPA
                        <input
                            data-c="education"
                            data-i="${i}"
                            data-k="grade"
                            value="${esc(x.grade)}">
                    </label>

                </div>
            `)
        ).join('');


    document.getElementById('experienceItems').innerHTML =
        state.experience.map((x, i) =>
            item('Experience', `

                <div class="item-grid">

                    <label>
                        Company
                        <input
                            data-c="experience"
                            data-i="${i}"
                            data-k="company"
                            value="${esc(x.company)}">
                    </label>

                    <label>
                        Role
                        <input
                            data-c="experience"
                            data-i="${i}"
                            data-k="role"
                            value="${esc(x.role)}">
                    </label>

                    <label>
                        Start (year)
                        <input
                            data-c="experience"
                            data-i="${i}"
                            data-k="start_year"
                            value="${esc(x.start_year)}">
                    </label>

                    <label>
                        End (year or Present)
                        <input
                            data-c="experience"
                            data-i="${i}"
                            data-k="end_year"
                            value="${esc(x.end_year)}">
                    </label>

                </div>

                <label>
                    Responsibilities & impact

                    <textarea
                        rows="5"
                        data-c="experience"
                        data-i="${i}"
                        data-k="responsibilities">${esc(x.responsibilities)}</textarea>
                </label>

            `)
        ).join('');


    document.getElementById('skillItems').innerHTML =
        state.skills.map((x, i) =>
            item('Skill', `

                <label>
                    Skill

                    <input
                        data-c="skills"
                        data-i="${i}"
                        data-k="skill"
                        value="${esc(x.skill)}">
                </label>

                <div class="field-head">

                    <label>Description</label>

                    <button
                        type="button"
                        class="generate"
                        onclick="generateSkill(${i})">
                        ✧ Generate
                    </button>

                </div>

                <textarea
                    rows="3"
                    data-c="skills"
                    data-i="${i}"
                    data-k="description">${esc(x.description)}</textarea>

            `)
        ).join('');


    document.getElementById('projectItems').innerHTML =
        state.projects.map((x, i) =>
            item('Project', `

                <div class="item-grid">

                    <label>
                        Project name

                        <input
                            data-c="projects"
                            data-i="${i}"
                            data-k="project_name"
                            value="${esc(x.project_name)}">
                    </label>

                    <label>
                        Tech stack

                        <input
                            data-c="projects"
                            data-i="${i}"
                            data-k="tech_stack"
                            value="${esc(x.tech_stack)}">
                    </label>

                    <label>
                        Relevance to role (0–10)

                        <input
                            type="number"
                            min="0"
                            max="10"
                            data-c="projects"
                            data-i="${i}"
                            data-k="relevance"
                            value="${esc(x.relevance)}">
                    </label>

                </div>

                <div class="field-head">

                    <label>Description</label>

                    <button
                        type="button"
                        class="generate"
                        onclick="generateProject(${i})">
                        ✧ Generate
                    </button>

                </div>

                <textarea
                    rows="4"
                    data-c="projects"
                    data-i="${i}"
                    data-k="description">${esc(x.description)}</textarea>

            `)
        ).join('');


    document.getElementById('certItems').innerHTML =
        state.certifications.map((x, i) =>
            item('Certification', `

                <div class="item-grid">

                    <label>
                        Certification

                        <input
                            data-c="certifications"
                            data-i="${i}"
                            data-k="certification"
                            value="${esc(x.certification)}">
                    </label>

                    <label>
                        Issuer

                        <input
                            data-c="certifications"
                            data-i="${i}"
                            data-k="issuer"
                            value="${esc(x.issuer)}">
                    </label>

                    <label>
                        Year

                        <input
                            data-c="certifications"
                            data-i="${i}"
                            data-k="year"
                            value="${esc(x.year)}">
                    </label>

                </div>

            `)
        ).join('');


    bindCollectionInputs();
}


function bindCollectionInputs() {

    document.querySelectorAll('[data-c]').forEach(el => {

        const handler = () => {

            const collection = el.dataset.c;
            const index = Number(el.dataset.i);
            const key = el.dataset.k;

            if (!state[collection]) return;
            if (!state[collection][index]) return;

            state[collection][index][key] = el.value;

            updatePreview();
            updateMetrics();
            scheduleSave();
        };

        el.oninput = handler;
        el.onchange = handler;
    });
}


function bindMainInputs() {

    const names = [
        'full_name',
        'target_role',
        'email',
        'phone',
        'location',
        'website',
        'github',
        'linkedin',
        'summary',
        'objective'
    ];

    names.forEach(name => {

        const el = document.querySelector(`[name="${name}"]`);

        if (!el) return;

        const handler = () => {

            state[name] = el.value;

            updatePreview();
            updateMetrics();
            scheduleSave();
        };

        el.addEventListener('input', handler);
        el.addEventListener('change', handler);
    });
}


function addEducation() {

    state.education.push({
        institution: '',
        degree: '',
        field_of_study: '',
        level: "Bachelor's",
        start_year: '',
        end_year: '',
        grade: ''
    });

    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


function addExperience() {

    state.experience.push({
        company: '',
        role: '',
        start_year: '',
        end_year: '',
        responsibilities: ''
    });

    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


function addSkill() {

    state.skills.push({
        skill: '',
        description: ''
    });

    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


function addProject() {

    state.projects.push({
        project_name: '',
        tech_stack: '',
        relevance: 0,
        description: ''
    });

    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


function addCertification() {

    state.certifications.push({
        certification: '',
        issuer: '',
        year: ''
    });

    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


window.addEducation = addEducation;
window.addExperience = addExperience;
window.addSkill = addSkill;
window.addProject = addProject;
window.addCertification = addCertification;


let saveTimer = null;


function scheduleSave() {

    clearTimeout(saveTimer);

    const saveState = document.getElementById('saveState');

    if (saveState) {
        saveState.textContent = 'Saving…';
    }

    saveTimer = setTimeout(() => {
        save();
    }, 700);
}


async function save() {

    try {

        state.title =
            document.getElementById('resumeTitle').value;

        state.template =
            document.getElementById('templateSelect').value;

        const result = await api(
            '/api/resumes/' + state.id,
            {
                method: 'PUT',
                body: JSON.stringify(state)
            }
        );

        const saveState =
            document.getElementById('saveState');

        if (saveState) {
            saveState.textContent = 'Saved';
        }

        return true;

    } catch (e) {

        console.error('Save failed:', e);

        const saveState =
            document.getElementById('saveState');

        if (saveState) {
            saveState.textContent = 'Save failed';
        }

        return false;
    }
}


function sync() {

    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


function updateMetrics() {

    const checks = [
        state.full_name,
        state.email,
        state.phone,
        state.location,
        state.target_role,
        state.summary,
        state.objective,
        state.education.length,
        state.experience.length,
        state.skills.length,
        state.projects.length,
        state.certifications.length
    ];

    const filled =
        checks.filter(Boolean).length;

    const comp =
        Math.round(
            filled / checks.length * 100
        );

    const value =
        document.getElementById('completeValue');

    const bar =
        document.getElementById('completeBar');

    if (value) {
        value.textContent = comp + '%';
    }

    if (bar) {
        bar.style.width = comp + '%';
    }

    const metric =
        document.getElementById('mComp');

    if (metric) {
        metric.textContent = comp;
    }
}


/* =========================================================
   CONTACT ICON HELPERS
   ========================================================= */

function cleanPhone(value) {

    return String(value || '')
        .replace(/[^0-9+]/g, '');
}


function safeUrl(value) {

    const v =
        String(value || '').trim();

    if (!v) {
        return '';
    }

    return /^https?:\/\//i.test(v)
        ? v
        : 'https://' + v;
}


/* =========================================================
   SVG CONTACT ICONS
   ========================================================= */

function contactIcons() {

    return `

        ${state.email ? `
            <a
                href="mailto:${esc(state.email)}"
                class="contact-icon"
                title="Email"
                aria-label="Email">

                <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true">

                    <rect
                        x="2.5"
                        y="5"
                        width="19"
                        height="14"
                        rx="1.5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8">
                    </rect>

                    <path
                        d="M3.5 6.5L12 13.2L20.5 6.5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round">
                    </path>

                </svg>

            </a>
        ` : ''}


        ${state.phone ? `
            <a
                href="tel:${esc(cleanPhone(state.phone))}"
                class="contact-icon"
                title="Phone"
                aria-label="Phone">

                <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true">

                    <path
                        d="M6.7 2.8L9.4 2.2C10 2.1 10.6 2.4 10.9 3L12.4 6.5C12.6 7 12.5 7.6 12.1 8L10.4 9.7C11.3 11.6 12.4 12.7 14.3 13.6L16 11.9C16.4 11.5 17 11.4 17.5 11.6L21 13.1C21.6 13.4 21.9 14 21.8 14.6L21.2 17.3C21.1 18 20.5 18.5 19.8 18.5C11.7 18.5 5.5 12.3 5.5 4.2C5.5 3.5 6 2.9 6.7 2.8Z"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        stroke-linecap="round"
                        stroke-linejoin="round">
                    </path>

                </svg>

            </a>
        ` : ''}


        ${state.location ? `
            <span
                class="contact-location"
                title="${esc(state.location)}">

                ${esc(state.location)}

            </span>
        ` : ''}


        ${state.website ? `
            <a
                href="${esc(safeUrl(state.website))}"
                target="_blank"
                rel="noopener noreferrer"
                class="contact-icon"
                title="Website / Portfolio"
                aria-label="Website">

                <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true">

                    <circle
                        cx="12"
                        cy="12"
                        r="9.5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7">
                    </circle>

                    <path
                        d="M2.8 12H21.2"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7">
                    </path>

                    <path
                        d="M12 2.5C14.5 5.2 15.5 8.4 15.5 12S14.5 18.8 12 21.5C9.5 18.8 8.5 15.6 8.5 12S9.5 5.2 12 2.5Z"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7">
                    </path>

                </svg>

            </a>
        ` : ''}


        ${state.github ? `
            <a
                href="${esc(safeUrl(state.github))}"
                target="_blank"
                rel="noopener noreferrer"
                class="contact-icon"
                title="GitHub"
                aria-label="GitHub">

                <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true">

                    <path
                        fill="currentColor"
                        d="M12 .7A11.3 11.3 0 0 0 8.4 22.8c.6.1.8-.3.8-.6v-2.1c-3.1.7-3.8-1.3-3.8-1.3-.5-1.3-1.2-1.7-1.2-1.7-1-.8.1-.8.1-.8 1.1.1 1.7 1.2 1.7 1.2 1 .1 1.9-.8 2.1-1.3.1-.8.4-1.2.7-1.5-2.5-.3-5.1-1.3-5.1-5.5 0-1.2.4-2.2 1.1-3-.1-.3-.5-1.4.1-2.9 0 0 .9-.3 3 1.1a10.5 10.5 0 0 1 5.5 0c2.1-1.4 3-1.1 3-1.1.6 1.5.2 2.6.1 2.9.7.8 1.1 1.8 1.1 3 0 4.2-2.6 5.2-5.1 5.5.4.4.7 1 .7 2v2.9c0 .3.2.7.8.6A11.3 11.3 0 0 0 12 .7Z">
                    </path>

                </svg>

            </a>
        ` : ''}


        ${state.linkedin ? `
            <a
                href="${esc(safeUrl(state.linkedin))}"
                target="_blank"
                rel="noopener noreferrer"
                class="contact-icon"
                title="LinkedIn"
                aria-label="LinkedIn">

                <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true">

                    <path
                        fill="currentColor"
                        d="M4.7 3.5A2.2 2.2 0 1 1 4.7 7.9A2.2 2.2 0 0 1 4.7 3.5ZM2.8 9.2H6.6V21H2.8V9.2ZM8.7 9.2H12.3V10.8H12.4C12.9 9.9 14.1 8.8 16.1 8.8C20 8.8 20.7 11.4 20.7 14.8V21H16.9V15.5C16.9 14.2 16.9 12.6 15 12.6C13.1 12.6 12.6 14 12.6 15.4V21H8.7V9.2Z">
                    </path>

                </svg>

            </a>
        ` : ''}

    `;
}


/* =========================================================
   RESUME PREVIEW
   ========================================================= */

function previewContent() {

    const skills =
        state.skills
            .filter(x => x.skill)
            .map(x => `
                <div class="r-item">

                    <b>
                        ${esc(x.skill).toUpperCase()}
                    </b>

                    <p>
                        ${esc(x.description)}
                    </p>

                </div>
            `)
            .join('');


    const certs =
        state.certifications
            .filter(x => x.certification)
            .map(x => `
                <div class="r-item">

                    <b>
                        ${esc(x.certification).toUpperCase()}
                    </b>

                    <p>
                        ${esc(x.issuer)}
                        ${x.year ? ' · ' + esc(x.year) : ''}
                    </p>

                </div>
            `)
            .join('');


    const edu =
        state.education
            .filter(x => x.institution || x.degree)
            .map(x => `
                <div class="r-item">

                    <div class="r-title">

                        <b>
                            ${esc(x.degree).toUpperCase()}

                            ${x.field_of_study
                                ? ', ' +
                                  esc(x.field_of_study).toUpperCase()
                                : ''}
                        </b>

                        <span>
                            ${esc(x.start_year)}
                            —
                            ${esc(x.end_year)}
                        </span>

                    </div>

                    <p>
                        ${esc(x.institution)}
                        ${x.grade ? ' · ' + esc(x.grade) : ''}
                    </p>

                </div>
            `)
            .join('');


    const exp =
        state.experience
            .filter(x => x.company || x.role)
            .map(x => `
                <div class="r-item">

                    <div class="r-title">

                        <b>
                            ${esc(x.role).toUpperCase()}

                            ${x.company
                                ? ' · ' +
                                  esc(x.company).toUpperCase()
                                : ''}
                        </b>

                        <span>
                            ${esc(x.start_year)}
                            —
                            ${esc(x.end_year)}
                        </span>

                    </div>

                    <p>
                        ${esc(x.responsibilities)}
                    </p>

                </div>
            `)
            .join('');


    const projects =
        state.projects
            .filter(x => x.project_name)
            .map(x => `
                <div class="r-item">

                    <div class="r-title">

                        <b>
                            ${esc(x.project_name).toUpperCase()}
                        </b>

                        <span>
                            ${esc(x.tech_stack).toUpperCase()}
                        </span>

                    </div>

                    <p>
                        ${esc(x.description)}
                    </p>

                </div>
            `)
            .join('');


    return `

        <header class="r-head">

            <div>

                <h1>
                    ${esc(state.full_name || 'YOUR NAME')}
                </h1>

                <p>
                    ${esc(state.target_role || 'TARGET ROLE')}
                </p>

            </div>


            <div class="r-contact">

                ${contactIcons()}

            </div>

        </header>


        <div class="r-columns">

            <main>

                ${
                    state.summary
                        ? `
                            <section>

                                <h3>
                                    PROFESSIONAL SUMMARY
                                </h3>

                                <p>
                                    ${esc(state.summary)}
                                </p>

                            </section>
                        `
                        : ''
                }


                ${
                    state.objective
                        ? `
                            <section>

                                <h3>
                                    CAREER OBJECTIVE
                                </h3>

                                <p>
                                    ${esc(state.objective)}
                                </p>

                            </section>
                        `
                        : ''
                }


                ${
                    exp
                        ? `
                            <section>

                                <h3>
                                    EXPERIENCE
                                </h3>

                                ${exp}

                            </section>
                        `
                        : ''
                }


                ${
                    projects
                        ? `
                            <section>

                                <h3>
                                    PROJECTS
                                </h3>

                                ${projects}

                            </section>
                        `
                        : ''
                }


                ${
                    edu
                        ? `
                            <section>

                                <h3>
                                    EDUCATION
                                </h3>

                                ${edu}

                            </section>
                        `
                        : ''
                }

            </main>


            <aside>

                ${
                    skills
                        ? `
                            <section>

                                <h3>
                                    SKILLS
                                </h3>

                                ${skills}

                            </section>
                        `
                        : ''
                }


                ${
                    certs
                        ? `
                            <section>

                                <h3>
                                    CERTIFICATIONS
                                </h3>

                                ${certs}

                            </section>
                        `
                        : ''
                }

            </aside>

        </div>

    `;
}


function updatePreview() {

    const p =
        document.getElementById('resumePreview');

    if (!p) return;

    const template =
        document.getElementById('templateSelect').value;

    p.className =
        'resume-preview ' + template;

    p.innerHTML =
        previewContent();
}


/* =========================================================
   TABS
   ========================================================= */

document.querySelectorAll('.tab').forEach(tab => {

    tab.onclick = () => {

        document
            .querySelectorAll('.tab')
            .forEach(x =>
                x.classList.remove('active')
            );

        document
            .querySelectorAll('.panel')
            .forEach(x =>
                x.classList.remove('active')
            );

        tab.classList.add('active');

        const panel =
            document.querySelector(
                `[data-panel="${tab.dataset.tab}"]`
            );

        if (panel) {
            panel.classList.add('active');
        }
    };

});


/* =========================================================
   TEMPLATE SELECT
   ========================================================= */

document.getElementById('templateSelect').onchange = () => {

    state.template =
        document.getElementById('templateSelect').value;

    updatePreview();
    scheduleSave();
};


/* =========================================================
   RESUME TITLE
   ========================================================= */

document.getElementById('resumeTitle').oninput = () => {

    state.title =
        document.getElementById('resumeTitle').value;

    scheduleSave();
};


/* =========================================================
   EVALUATE RESUME
   ========================================================= */

document.getElementById('evaluateBtn').onclick = async () => {

    const saved = await save();

    if (!saved) {

        alert(
            'Please wait until the resume is saved before evaluating.'
        );

        return;
    }


    try {

        const d =
            await api(
                '/api/resumes/' +
                state.id +
                '/evaluate',
                {
                    method: 'POST',
                    body: '{}'
                }
            );


        document.getElementById(
            'categoryBadge'
        ).textContent = d.category;


        document.getElementById(
            'confidence'
        ).textContent =
            d.confidence + '%';


        document.getElementById(
            'rubric'
        ).textContent =
            d.rubric + '/100';


        const ids = [
            'mSkills',
            'mExp',
            'mEdu',
            'mCert',
            'mProj',
            'mComp'
        ];


        const indexes = [
            0,
            1,
            2,
            3,
            4,
            5
        ];


        ids.forEach((id, i) => {

            const el =
                document.getElementById(id);

            if (el && d.features) {

                el.textContent =
                    d.features[indexes[i]];
            }

        });


        const recommendations =
            document.getElementById(
                'recommendations'
            );


        if (
            recommendations &&
            Array.isArray(d.recommendations)
        ) {

            recommendations.innerHTML =
                d.recommendations
                    .map(x =>
                        `<li>${esc(x)}</li>`
                    )
                    .join('');
        }


    } catch (e) {

        console.error(
            'Evaluation failed:',
            e
        );

        alert(e.message);
    }
};


/* =========================================================
   GENERATIVE AI
   ========================================================= */

async function generate(kind, payload) {

    try {

        const d =
            await api(
                '/api/generate',
                {
                    method: 'POST',

                    body: JSON.stringify({
                        kind,
                        payload
                    })
                }
            );

        return d.text;

    } catch (e) {

        console.error(
            'AI generation failed:',
            e
        );

        alert(e.message);

        return null;
    }
}


/* =========================================================
   SUMMARY / OBJECTIVE GENERATION
   ========================================================= */

document
    .querySelectorAll('.generate')
    .forEach(button => {

        button.onclick = async () => {

            const kind =
                button.dataset.kind;

            if (!kind) return;


            const text =
                await generate(
                    kind,
                    {
                        target_role:
                            state.target_role,

                        full_name:
                            state.full_name,

                        skills:
                            state.skills,

                        experience:
                            state.experience,

                        education:
                            state.education,

                        projects:
                            state.projects
                    }
                );


            if (!text) return;


            const field =
                kind === 'summary'
                    ? 'summary'
                    : 'objective';


            state[field] =
                text;


            const input =
                document.querySelector(
                    `[name="${field}"]`
                );


            if (input) {
                input.value = text;
            }


            updatePreview();
            updateMetrics();
            scheduleSave();
        };

    });


/* =========================================================
   GENERATE SKILL DESCRIPTION
   ========================================================= */

async function generateSkill(i) {

    if (!state.skills[i]) return;


    const text =
        await generate(
            'skill',
            {
                target_role:
                    state.target_role,

                skill:
                    state.skills[i].skill,

                experience:
                    state.experience
            }
        );


    if (!text) return;


    state.skills[i].description =
        text;


    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


/* =========================================================
   GENERATE PROJECT DESCRIPTION
   ========================================================= */

async function generateProject(i) {

    if (!state.projects[i]) return;


    const x =
        state.projects[i];


    const text =
        await generate(
            'project',
            {
                target_role:
                    state.target_role,

                project_name:
                    x.project_name,

                tech_stack:
                    x.tech_stack,

                description:
                    x.description
            }
        );


    if (!text) return;


    state.projects[i].description =
        text;


    renderCollections();
    updatePreview();
    updateMetrics();
    scheduleSave();
}


window.generateSkill =
    generateSkill;

window.generateProject =
    generateProject;


/* =========================================================
   INITIALIZE
   ========================================================= */

bindMainInputs();

renderCollections();

updatePreview();

updateMetrics();