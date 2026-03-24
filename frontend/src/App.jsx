import { useState } from 'react'

const EXAMPLES = [
  'Convert 5 kilograms to pounds',
  'How many liters are 3 gallons?',
  'Convert 10 meters to feet',
  'Convert 98 fahrenheit to celsius',
  'Convert 60 mph to km/h',
  'Convert 150 pounds to kilograms',
]

export default function App() {
  const [userInput, setUserInput] = useState(EXAMPLES[0])
  const [model, setModel] = useState('llama3.2:3b')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput, model }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'The conversion failed.')
      }

      setResult(data)
    } catch (requestError) {
      setResult(null)
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Artificial Intelligence Applications</p>
        <h1>Unit Conversion Agent</h1>
        <p className="lede">
          A React frontend and FastAPI backend where an Ollama-powered agent selects
          conversion tools from natural-language requests.
        </p>
      </section>

      <section className="panel">
        <form onSubmit={handleSubmit} className="converter-form">
          <label>
            Request
            <textarea
              value={userInput}
              onChange={(event) => setUserInput(event.target.value)}
              rows={4}
              placeholder="Convert 5 kilograms to pounds"
            />
          </label>

          <label>
            Ollama model
            <input
              value={model}
              onChange={(event) => setModel(event.target.value)}
              placeholder="llama3.2:3b"
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? 'Converting...' : 'Run conversion'}
          </button>
        </form>

        <div className="examples">
          <h2>Supported examples</h2>
          <div className="chip-grid">
            {EXAMPLES.map((example) => (
              <button
                type="button"
                key={example}
                className="chip"
                onClick={() => setUserInput(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}

      {result ? (
        <section className="result-grid">
          <article className="result-card primary">
            <p className="card-label">Result</p>
            <h2>
              {result.result.output_value} {result.result.output_unit}
            </h2>
            <p>
              From {result.result.input_value} {result.result.input_unit}
            </p>
          </article>

          <article className="result-card">
            <p className="card-label">Agent</p>
            <h3>{result.tool_call.tool_name}</h3>
            <p>{result.agent_reasoning}</p>
          </article>

          <article className="result-card">
            <p className="card-label">Formula</p>
            <h3>{result.result.formula}</h3>
            <p>{result.explanation}</p>
          </article>
        </section>
      ) : null}
    </main>
  )
}
