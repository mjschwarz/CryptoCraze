import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from 'react-bootstrap';
import Transaction from './Transaction';
import { API_BASE_URL, SECONDS_JS } from '../config';
import history from '../history';

const POLL_INTERVAL = 10 * SECONDS_JS;

function TransactionPool() {
  const [transactions, setTransactions] = useState([]);

const fetchTransactions = () => {
  fetch(`${API_BASE_URL}/transactions`)
    .then(response => response.json())
    .then(json => {
      console.log('transactions json', json);
      setTransactions(json);
    });
}

  useEffect(() => {
    fetchTransactions();
    // Fetch/update transaction pool every 10 seconds
    const intervalId = setInterval(fetchTransactions, POLL_INTERVAL);
    return () => clearInterval(intervalId);
  }, []);

  const fetchMineBlock = () => {
    fetch(`${API_BASE_URL}/blockchain/mine`)
      .then(() => {
        alert('Mining has begun!');
        history.push('/blockchain');
      })
  }

  return (
    <div className="TransactionPool">
      <Link to="/">Home</Link>
      <Link to="/blockchain">Blockchain</Link>
      <Link to="/conduct-transaction">Conduct a Transaction</Link>
      <h3>Transaction Pool</h3>
      <div>
        {
          transactions.map(transaction => (
            <div key={transaction.id}>
              <hr />
              <Transaction transaction={transaction} />
            </div>
          ))
        }
      </div>
      <hr />
      <Button variant="danger" onClick={fetchMineBlock}>Mine a block of these transactions. Earn 50 coins!</Button>
    </div>
  )
}

export default TransactionPool;
