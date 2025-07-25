import os
import json
import datetime
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from groq import Groq
from .models import Player, GameScenario, GameSession, GameLog

# --- AI Client and Prompt Setup ---

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
client = Groq(api_key=api_key)

def load_json_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

SYSTEM_PROMPT = load_json_from_file('prompt_template.json').get('trpg_system_prompt', {})
GAME_RULES = load_json_from_file('game_rules.json').get('cyberpunk_trpg_rules', {})
MAJOR_PLOT_POINTS = load_json_from_file('major_plot_points.json')

# --- Views ---

def scenario_list(request):
    scenarios = GameScenario.objects.all()
    return render(request, 'trpg/scenario_list.html', {'scenarios': scenarios})

def start_game(request, scenario_id):
    if request.method == 'POST':
        player_name = request.POST.get('player_name')
        if not player_name:
            return HttpResponseBadRequest("Player name is required.")

        scenario = get_object_or_404(GameScenario, pk=scenario_id)
        player, _ = Player.objects.get_or_create(name=player_name)
        session, created = GameSession.objects.get_or_create(player=player, scenario=scenario)
        
        if created:
            session.current_plot_point_id = "start_of_game"
            session.save()
            initial_message = scenario.initial_prompt.replace("{{player_name}}", player_name)
            GameLog.objects.create(
                session=session, 
                message=initial_message,
                is_major_decision=True, 
                is_sent_by_user=False
            )
            
        return redirect('game_session', session_id=session.id)
    
    return redirect('scenario_list')

def game_session(request, session_id):
    session = get_object_or_404(GameSession, pk=session_id)
    logs = session.logs.all().order_by('timestamp')
    for log in logs:
        log.is_user_message = log.is_sent_by_user
    return render(request, 'trpg/game_session.html', {'session': session, 'logs': logs})

def send_message(request, session_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    session = get_object_or_404(GameSession, pk=session_id)
    data = json.loads(request.body)
    user_message_text = data.get('message')
    is_major_choice = data.get('is_major', False)
    next_point_id = data.get('next_point_id', None)

    if not user_message_text:
        return JsonResponse({'error': 'Message not provided'}, status=400)

    # 1. Save user log and update session state from user's choice
    user_log = GameLog.objects.create(session=session, message=user_message_text, is_sent_by_user=True, is_major_decision=is_major_choice)
    session.current_plot_point_id = next_point_id
    session.save()

    # 2. Construct a concise prompt for the AI
    # Use a summary of the current situation + last few messages
    context_summary = f"Current situation: {session.current_plot_point_id or 'free-roaming'}. Player state: {session.player_state}."

    recent_logs = session.logs.all().order_by('-timestamp')[:4] # Last 4 messages
    conversation_history = []
    for log in reversed(recent_logs):
        role = "user" if log.is_sent_by_user else "assistant"
        conversation_history.append({"role": role, "content": log.message})

    prompt_elements = [
        SYSTEM_PROMPT,
        GAME_RULES,
        {"role": "system", "content": context_summary}
    ]
    # Filter out any empty dictionaries or ones without content to prevent API errors
    valid_prompts = [p for p in prompt_elements if p and p.get('content')]

    messages_to_send = valid_prompts + conversation_history

    # 3. Call AI and get response
    try:
        completion = client.chat.completions.create(
            model="compound-beta",
            messages=messages_to_send,
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        ai_response_raw = completion.choices[0].message.content
        ai_response_json = json.loads(ai_response_raw)
        description = ai_response_json.get("description", "(내용 없음)")

    except Exception as e:
        description = f"AI 응답 생성 중 오류: {e}"
        ai_response_json = {}

    # 4. Save AI log
    ai_log = GameLog.objects.create(session=session, message=description, is_sent_by_user=False)

    # 5. Determine next actions based on keywords or AI suggestions
    next_actions = []
    triggered_plot_point = False

    # Check if AI response triggers a new plot point
    for point_id, point_data in MAJOR_PLOT_POINTS.items():
        if any(keyword.lower() in description.lower() for keyword in point_data.get('keywords', [])):
            session.current_plot_point_id = point_id
            if "gives_items" in point_data:
                # This is a simple example; you might want more complex state management
                current_items = session.player_state.get('inventory', [])
                current_items.extend(point_data["gives_items"])
                session.player_state['inventory'] = list(set(current_items)) # Remove duplicates
            session.save()
            next_actions = point_data.get('choices', [])
            triggered_plot_point = True
            break

    # If no plot point was triggered by keywords
    if not triggered_plot_point:
        if session.current_plot_point_id and session.current_plot_point_id in MAJOR_PLOT_POINTS:
            # Use the choices from the current plot point if they exist
            next_actions = MAJOR_PLOT_POINTS[session.current_plot_point_id].get('choices', [])
        else:
            # Fallback to AI-generated choices for free-roaming
            next_actions = ai_response_json.get("next_action_options", [])

    return JsonResponse({
        'user_message': {'message': user_log.message, 'timestamp': user_log.timestamp.strftime('%H:%M')},
        'ai_message': {'message': ai_log.message, 'timestamp': ai_log.timestamp.strftime('%H:%M')},
        'next_action_options': next_actions
    })

def log_view(request, session_id):
    session = get_object_or_404(GameSession, pk=session_id)
    major_logs = session.logs.filter(is_major_decision=True).order_by('timestamp')
    return render(request, 'trpg/log_list.html', {'session': session, 'major_logs': major_logs})