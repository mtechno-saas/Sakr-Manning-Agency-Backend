// components/dashboard/Dashboard.jsx
import React from "react";
import {
  Ship,
  Users,
  BarChart3,
  Settings,
  Bell,
  LogOut,
  MapPin,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import Button from "../ui/Button";
import { BUTTON_VARIANTS } from "../../utils/constants";

const Dashboard = ({ user, onLogout }) => {
  // Sample data for demonstration
  const stats = [
    {
      title: "Active Vessels",
      value: "24",
      change: "+2",
      icon: Ship,
      color: "blue",
    },
    {
      title: "Total Crew",
      value: "348",
      change: "+12",
      icon: Users,
      color: "green",
    },
    {
      title: "Revenue",
      value: "$2.4M",
      change: "+8%",
      icon: TrendingUp,
      color: "purple",
    },
    {
      title: "Ports",
      value: "15",
      change: "+1",
      icon: MapPin,
      color: "orange",
    },
  ];

  const recentActivities = [
    {
      id: 1,
      type: "success",
      message: "MV Atlantic Star arrived at Port of Singapore",
      time: "2 hours ago",
    },
    {
      id: 2,
      type: "warning",
      message: "Maintenance scheduled for MV Pacific Dawn",
      time: "4 hours ago",
    },
    {
      id: 3,
      type: "info",
      message: "New crew member assigned to MV Ocean Explorer",
      time: "6 hours ago",
    },
    {
      id: 4,
      type: "success",
      message: "Cargo loading completed at Rotterdam",
      time: "8 hours ago",
    },
  ];

  const getActivityIcon = (type) => {
    switch (type) {
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case "error":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <Bell className="w-5 h-5 text-blue-500" />;
    }
  };

  const getStatColor = (color) => {
    const colors = {
      blue: "bg-blue-500",
      green: "bg-green-500",
      purple: "bg-purple-500",
      orange: "bg-orange-500",
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Title */}
            <div className="flex items-center">
              <Ship className="w-8 h-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">
                Sakr Maritime
              </h1>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Bell className="w-6 h-6" />
              </button>

              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {user.name}
                  </p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>

                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>

              <Button
                onClick={onLogout}
                variant={BUTTON_VARIANTS.GHOST}
                size="sm"
                leftIcon={LogOut}
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user.name.split(" ")[0]}!
          </h2>
          <p className="text-gray-600">
            Here's what's happening with your maritime operations today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="bg-white rounded-xl p-6 shadow-sm border"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg ${getStatColor(stat.color)}`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                    {stat.change}
                  </span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-1">
                  {stat.value}
                </h3>
                <p className="text-sm text-gray-600">{stat.title}</p>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Activities */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Recent Activities
                </h3>
                <Button variant={BUTTON_VARIANTS.GHOST} size="sm">
                  View All
                </Button>
              </div>
            </div>

            <div className="p-6">
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3">
                    {getActivityIcon(activity.type)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">
                        {activity.message}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                Quick Actions
              </h3>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <Button fullWidth leftIcon={Ship} className="h-16 flex-col">
                  <span>Add Vessel</span>
                </Button>

                <Button
                  variant={BUTTON_VARIANTS.SECONDARY}
                  fullWidth
                  leftIcon={Users}
                  className="h-16 flex-col"
                >
                  <span>Manage Crew</span>
                </Button>

                <Button
                  variant={BUTTON_VARIANTS.SECONDARY}
                  fullWidth
                  leftIcon={BarChart3}
                  className="h-16 flex-col"
                >
                  <span>View Reports</span>
                </Button>

                <Button
                  variant={BUTTON_VARIANTS.SECONDARY}
                  fullWidth
                  leftIcon={Settings}
                  className="h-16 flex-col"
                >
                  <span>Settings</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
