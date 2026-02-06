

# Company Q&A Chat Dashboard

## Overview
A modern, colorful dashboard interface for a company Q&A chat platform where employees can ask questions to different departments and receive visually distinct responses.

---

## 🎨 Design Direction
- **Style**: Colorful & branded with vibrant department-specific colors
- **Layout**: Sidebar + main chat panel design
- **Department visual treatment**: Color-coded left borders with department badges and icons

### Department Color Scheme
- **Engineering** - Blue with code/gear icon
- **Delivery** - Orange with truck/package icon
- **Admin** - Purple with settings/clipboard icon
- **Sales** - Green with chart/handshake icon
- **C-Level** - Gold/amber with briefcase/star icon
- **Marketing** - Pink/magenta with megaphone icon

---

## 📐 Layout Structure

### Sidebar (Left)
1. **Company Logo & Title** at the top
2. **User Profile Section** - Avatar, name, role
3. **Department Selector** - Dropdown or list to choose which department to ask
4. **Chat History List** - Previous conversations with department indicator and preview text
5. **New Chat Button** - Start a fresh conversation

### Main Panel (Right)
1. **Header** - Current department name with colored badge, chat title
2. **Chat Messages Area**
   - User messages aligned right (neutral styling)
   - Department responses aligned left with:
     - Colored left border
     - Department badge with icon
     - Timestamp
     - Optional avatar
3. **Message Input Area**
   - Text input field
   - Send button
   - Quick reply suggestions (optional chips)

---

## 💬 Chat Functionality

### Message Flow
1. User selects a department from the sidebar
2. User types a question and sends it
3. After a short delay (1-2 seconds), a mock response automatically appears from the selected department
4. Messages display with proper alignment and department styling

### Example Conversations (Pre-built demos)
Each department will have sample Q&A exchanges:
- **Engineering**: "How do I request API access?" → Technical response
- **Sales**: "What's our current pricing structure?" → Sales-focused response
- **Marketing**: "When is the next product launch?" → Marketing timeline
- **Admin**: "How do I submit expense reports?" → Process explanation
- **Delivery**: "What's the shipping timeline for priority orders?" → Logistics info
- **C-Level**: "What are our Q2 goals?" → Strategic overview

---

## ✨ Visual Polish
- Subtle entrance animation for new messages
- Smooth scrolling to latest message
- Department badge with icon appears on each response
- Timestamps on all messages
- Hover effects on interactive elements
- Loading indicator while "waiting" for response

---

## 📱 Responsive Considerations
- Sidebar collapses to icons on smaller screens
- Mobile-friendly chat input
- Touch-friendly department selection

