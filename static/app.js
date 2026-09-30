// EduGenie frontend: sends the form to the FastAPI backend and renders results.

const TASKS = {
  qa: {
    endpoint: "/qa", label: "Your question", title: "Answer",
    placeholder: "e.g. Which is the largest ocean?",
    body: (text) => ({ question: text }),
  },
  explain: {
    endpoint: "/explain", label: "Concept to explain", title: "Explanation", level: true,
    placeholder: "e.g. Photosynthesis",
    body: (text, level) => ({ concept: text, level }),
  },
  quiz: {
    endpoint: "/quiz", label: "Topic or passage", title: "Quiz",
    placeholder: "e.g. The Pythagoras Theorem — or paste a passage",
    body: (text) => ({ text }),
  },
  summarize: {
    endpoint: "/summarize", label: "Passage to summarise", title: "Summary",
    placeholder: "Paste a long paragraph or article here…",
    body: (text) => ({ text }),
  },
  learn: {
    endpoint: "/learn/recommendations", label: "What do you want to learn?", title: "Your learning path", level: true,
    placeholder: "e.g. SQL",
    body: (text, level) => ({ topic: text, level }),
  },
};

const form = document.getElementById("task-form");
const taskSelect = document.getElementById("task");
const levelRow = document.getElementById("level-row");
const levelSelect = document.getElementById("level");
const input = document.getElementById("input");
const inputLabel = document.getElementById("input-label");
const counter = document.getElementById("counter");
const submitBtn = document.getElementById("submit");
const result = document.getElementById("result");

// replaceChildren() would print "null" for skipped items, so filter them out.
const show = (...nodes) => result.replaceChildren(...nodes.filter((n) => n != null));

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) {
    if (child == null) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

function updateTask() {
  const task = TASKS[taskSelect.value];
  inputLabel.textContent = task.label;
  input.placeholder = task.placeholder;
  levelRow.hidden = !task.level;
}

function showLoading() {
  result.hidden = false;
  result.className = "card result";
  show(el("div", { class: "loading" }, el("div", { class: "spinner" }), "EduGenie is thinking…"));
}

function showError(message) {
  result.hidden = false;
  result.className = "card result error";
  show(el("strong", {}, "Something went wrong. "), message);
}

function renderText(title, text, source) {
  show(
    el("h2", {}, title),
    el("p", {}, text),
    source ? el("div", { class: "source" }, `Answered by ${source}`) : null,
  );
}

function renderQuiz(questions) {
  let answered = 0;
  let correct = 0;
  const score = el("div", { class: "score" }, `Score: 0 / ${questions.length}`);

  const items = questions.map((q, i) => {
    const feedback = el("div", { class: "feedback" });
    const buttons = q.options.map((opt) => el("button", { type: "button", class: "option" }, opt));
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const isRight = btn.textContent === q.answer;
        buttons.forEach((b) => {
          b.disabled = true;
          if (b.textContent === q.answer) b.classList.add("correct");
        });
        if (!isRight) btn.classList.add("wrong");
        answered += 1;
        if (isRight) correct += 1;
        feedback.textContent = (isRight ? "Correct! " : `Not quite — the answer is "${q.answer}". `) + (q.explanation || "");
        score.textContent = `Score: ${correct} / ${questions.length}` + (answered === questions.length ? " — quiz complete!" : "");
      });
    });
    return el("div", { class: "question" },
      el("h3", {}, `${i + 1}. ${q.question}`),
      el("div", { class: "options" }, ...buttons),
      feedback,
    );
  });

  show(el("h2", {}, "Quiz"), ...items, score);
}

function renderLearningPath(data) {
  const stages = (data.stages || []).map((s, i) =>
    el("div", { class: "stage" },
      el("h3", {}, `Stage ${i + 1}: ${s.title || ""}`),
      el("div", { class: "meta" },
        s.level ? el("span", { class: "badge" }, s.level) : null,
        s.duration ? `⏱ ${s.duration}` : null,
      ),
      s.concepts?.length ? el("ul", {}, ...s.concepts.map((c) => el("li", {}, c))) : null,
      s.practice ? el("p", {}, el("strong", {}, "Practice: "), s.practice) : null,
      s.resources?.length
        ? el("p", {}, el("strong", {}, "Resources: "),
            s.resources.map((r) => (r.type ? `${r.name} (${r.type})` : r.name)).join("; "))
        : null,
    ),
  );
  const tips = data.tips?.length
    ? [el("h3", {}, "Tips"), el("ul", {}, ...data.tips.map((t) => el("li", {}, t)))]
    : [];
  show(
    el("h2", {}, `Learning path: ${data.topic || ""}`),
    data.overview ? el("p", {}, data.overview) : null,
    ...stages,
    ...tips,
  );
}

async function handleSubmit(event) {
  event.preventDefault();
  const taskKey = taskSelect.value;
  const task = TASKS[taskKey];
  const text = input.value.trim();
  if (!text) return;

  submitBtn.disabled = true;
  showLoading();
  try {
    const response = await fetch(task.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(task.body(text, levelSelect.value)),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join("; ")
        : data.detail || `Server error (${response.status})`;
      throw new Error(detail);
    }
    result.className = "card result";
    if (taskKey === "quiz") renderQuiz(data.questions);
    else if (taskKey === "learn") renderLearningPath(data);
    else if (taskKey === "explain") renderText(task.title, data.explanation, data.source);
    else if (taskKey === "summarize") renderText(task.title, data.summary);
    else renderText(task.title, data.answer);
  } catch (err) {
    showError(err.message || "Please check your connection and try again.");
  } finally {
    submitBtn.disabled = false;
  }
}

taskSelect.addEventListener("change", updateTask);
input.addEventListener("input", () => { counter.textContent = `${input.value.length} characters`; });
form.addEventListener("submit", handleSubmit);
updateTask();
