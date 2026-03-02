from graph_builder import build_graph

app = build_graph()

state = {
    "image_url": "https://analysisstorage.blob.core.windows.net/images/sample3.jpg?sp=r&st=2026-03-02T17:29:05Z&se=2026-03-03T01:44:05Z&sv=2024-11-04&sr=b&sig=0bNJGJ4%2FW5SOUMw44Oo7yv3%2BWJw8ugRqO7OHEAyd9Cc%3D"
}

print("\n===== STREAMING EXECUTION =====\n")

for event in app.stream(state):
    print(event)
    print("--------------------------------------------------")
