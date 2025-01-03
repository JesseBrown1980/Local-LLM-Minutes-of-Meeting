import React from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
const bgImg = require("../assets/images/mom.png");
export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <img src={bgImg} alt="Meeting" className="mx-auto h-64 w-auto" />
          <div className="mt-8">
            <Link
              to="/upload"
              className="inline-flex items-center px-6 py-3 bg-[#aaaeda] hover:bg-[#ffd5fe] rounded-md text-lg"
            >
              <i className="bi bi-pen mr-2"></i>
              New Minutes of Meeting
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
