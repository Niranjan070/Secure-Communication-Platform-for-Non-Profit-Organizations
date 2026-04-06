(function () {
    if (!window.React || !window.ReactDOM) {
        return;
    }

    const e = React.createElement;

    function readJson(id) {
        const node = document.getElementById(id);
        if (!node) {
            return null;
        }
        try {
            return JSON.parse(node.textContent);
        } catch (_error) {
            return null;
        }
    }

    function StatCard(props) {
        return e(
            "div",
            { className: `stat-card stat-card-${props.accent}` },
            e("span", { className: `pill pill-${props.accent}` }, props.label),
            e("strong", null, String(props.value)),
            e("p", { className: "lede" }, props.description || "Live metric from the protected workspace.")
        );
    }

    function mountDashboard() {
        const rootNode = document.getElementById("dashboard-react-root");
        const data = readJson("dashboard-data");
        if (!rootNode || !data) {
            return;
        }

        function DashboardCards() {
            return e(
                "div",
                { className: "stat-grid" },
                data.cards.map((card) =>
                    e(StatCard, {
                        key: card.label,
                        label: card.label,
                        value: card.value,
                        accent: card.accent,
                    })
                )
            );
        }

        ReactDOM.createRoot(rootNode).render(e(DashboardCards));
    }

    function mountInbox() {
        const rootNode = document.getElementById("inbox-react-root");
        const data = readJson("inbox-data");
        if (!rootNode || !data) {
            return;
        }

        const cards = [
            { label: "Received", value: data.received, accent: "green" },
            { label: "Sent", value: data.sent, accent: "blue" },
            { label: "Valid Signatures", value: data.valid_signatures, accent: "orange" },
        ];

        function InboxCards() {
            return e(
                "div",
                { className: "stat-grid" },
                cards.map((card) =>
                    e(StatCard, {
                        key: card.label,
                        label: card.label,
                        value: card.value,
                        accent: card.accent,
                    })
                )
            );
        }

        ReactDOM.createRoot(rootNode).render(e(InboxCards));
    }

    function mountConcepts() {
        const rootNode = document.getElementById("concepts-react-root");
        const concepts = readJson("concepts-data");
        if (!rootNode || !concepts) {
            return;
        }

        function ConceptExplorer() {
            return e(
                "div",
                { className: "concept-list" },
                concepts.map((concept) =>
                    e(
                        "article",
                        { key: concept.id, className: "concept-card" },
                        e("p", { className: "eyebrow" }, concept.title),
                        e("p", { className: "lede" }, concept.summary),
                        e(
                            "ul",
                            null,
                            concept.points.map((point, index) => e("li", { key: `${concept.id}-${index}` }, point))
                        )
                    )
                )
            );
        }

        ReactDOM.createRoot(rootNode).render(e(ConceptExplorer));
    }

    mountDashboard();
    mountInbox();
    mountConcepts();
})();
