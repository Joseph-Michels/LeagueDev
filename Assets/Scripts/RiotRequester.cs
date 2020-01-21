using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
// using System.Threading.Tasks;
// using System;
// using System.Net;
// using System.Net.Http;
// using System.Net.Http.Headers;
// using System.IO;

public class RiotRequester : MonoBehaviour {
	void Start() {
		// A correct website page.
		StartCoroutine(GetRequest("https://na1.api.riotgames.com/lol/status/v3/shard-data"));

		// A non-existing page.
		StartCoroutine(GetRequest("https://error.html"));
	}

	IEnumerator GetRequest(string uri) {
		using(UnityWebRequest webRequest = UnityWebRequest.Get(uri)) {
			webRequest.SetRequestHeader("X-Riot-Token", "RGAPI-c40eda3c-45e1-4705-9dac-173ee2c4e14c");
			// Request and wait for the desired page.
			yield return webRequest.SendWebRequest();

			string[] pages = uri.Split('/');
			int page = pages.Length - 1;

			if(webRequest.isNetworkError) {
				Debug.Log(pages[page] + ": Error: " + webRequest.error);
			} else {
				Debug.Log(pages[page] + ":\nReceived: " + webRequest.downloadHandler.text);
			}
		}
	}

	/*
	private HttpClient client;
    void Awake() {
		client = new HttpClient(new HttpClientHandler { AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate });
		
		// below: tests
		client.BaseAddress = new Uri("https://na1.api.riotgames.com/");
		client.DefaultRequestHeaders.Authorization 
                         = new AuthenticationHeaderValue("X-Riot-Token", "RGAPI-c40eda3c-45e1-4705-9dac-173ee2c4e14c");
		HttpResponseMessage response = client.GetAsync("lol/status/v3/shard-data/").Result;
		response.EnsureSuccessStatusCode();
        string result = response.Content.ReadAsStringAsync().Result;
		Debug.Log(result);
	}
    void Start() {
        
    }

    void Update() {
        
    }

	public async Task<string> HttpGetAsync(string uri) {
		HttpWebRequest request = (HttpWebRequest)WebRequest.Create(uri);
		request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;

		using(HttpWebResponse response = (HttpWebResponse)await request.GetResponseAsync())
		using(Stream stream = response.GetResponseStream())
		using(StreamReader reader = new StreamReader(stream))
		{
			return await reader.ReadToEndAsync();
		}
	}*/
}
